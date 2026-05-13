"""
SQLite schema + connection helpers for the Easton pipeline.

Single source of truth for table definitions. Every phase imports from here.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import yaml
from dotenv import load_dotenv

# Load .env at import time so DATABASE_PATH is available
load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "pipeline.db"
CONFIG_DIR = REPO_ROOT / "config"


# ---------------------------------------------------------------------------
# Schema — keep this aligned with docs/ARCHITECTURE.md
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
-- PRAGMAs for sanity
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ---------- Phase 1 inputs ----------

CREATE TABLE IF NOT EXISTS states (
    state_code            TEXT PRIMARY KEY,
    state_name            TEXT NOT NULL,
    role_title            TEXT,                  -- "County Treasurer", etc.
    list_typically_free   INTEGER,               -- 1/0
    statute_citation      TEXT,
    notes                 TEXT,
    is_active             INTEGER DEFAULT 0,     -- only active states are run
    updated_at            TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS counties (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    state_code            TEXT NOT NULL,
    county_name           TEXT NOT NULL,
    fips_code             TEXT,                  -- 5-digit (state+county)
    role_title            TEXT,                  -- overrides state default if set
    contact_name          TEXT,
    contact_email         TEXT,
    contact_phone         TEXT,
    office_website        TEXT,
    list_format_known     TEXT,                  -- csv | xlsx | pdf | unknown
    list_cost_cents       INTEGER,               -- 0 = free
    list_request_method   TEXT,                  -- email | form | foia | phone
    notes                 TEXT,
    last_verified         TEXT,                  -- ISO date
    created_at            TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at            TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (state_code, county_name),
    FOREIGN KEY (state_code) REFERENCES states (state_code)
);
CREATE INDEX IF NOT EXISTS idx_counties_state ON counties (state_code);

-- ---------- Phase 2 outreach ----------

CREATE TABLE IF NOT EXISTS outreach_log (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    county_id             INTEGER NOT NULL,
    template_used         TEXT NOT NULL,
    sent_at               TEXT NOT NULL,
    message_id            TEXT,                  -- from Postmark
    status                TEXT NOT NULL,         -- see ARCHITECTURE.md for status values
    reply_received_at     TEXT,
    reply_summary         TEXT,
    attachment_path       TEXT,                  -- where we saved the sheet
    next_action           TEXT,                  -- wait | follow_up | send_payment | manual_review
    FOREIGN KEY (county_id) REFERENCES counties (id)
);
CREATE INDEX IF NOT EXISTS idx_outreach_county ON outreach_log (county_id);
CREATE INDEX IF NOT EXISTS idx_outreach_status ON outreach_log (status);

-- ---------- Phase 3 raw + filtered leads ----------

CREATE TABLE IF NOT EXISTS leads_raw (
    id                            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file                   TEXT NOT NULL,
    county_id                     INTEGER NOT NULL,
    received_date                 TEXT NOT NULL,
    raw_data                      TEXT NOT NULL,   -- JSON of original row
    parsed_owner_name             TEXT,
    parsed_parcel_id              TEXT,
    parsed_mailing_address        TEXT,
    parsed_property_address       TEXT,
    parsed_acres                  REAL,            -- nullable; often absent from county data
    parsed_delinquent_amount      REAL,
    imported_at                   TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (county_id) REFERENCES counties (id)
);
CREATE INDEX IF NOT EXISTS idx_raw_county ON leads_raw (county_id);
CREATE INDEX IF NOT EXISTS idx_raw_parcel ON leads_raw (parsed_parcel_id);

CREATE TABLE IF NOT EXISTS leads_filtered (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_lead_id              INTEGER NOT NULL UNIQUE,
    is_entity                INTEGER DEFAULT 0,           -- LLC/Corp/Trust match
    entity_match_pattern     TEXT,                        -- which pattern hit
    in_acre_range            INTEGER,                     -- NULL until Phase 4 if acres unknown
    passed_filters           INTEGER DEFAULT 0,           -- 1 if ready for Phase 4
    needs_zamplo_enrichment  INTEGER DEFAULT 1,
    filtered_at              TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_lead_id) REFERENCES leads_raw (id)
);
CREATE INDEX IF NOT EXISTS idx_filtered_passed ON leads_filtered (passed_filters);

-- ---------- Phase 4 Zamplo-enriched leads ----------

CREATE TABLE IF NOT EXISTS leads_enriched (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    filtered_lead_id         INTEGER NOT NULL UNIQUE,
    zamplo_parcel_id         TEXT,
    zamplo_acres             REAL,
    zamplo_estimated_value   REAL,
    zamplo_owner_data        TEXT,                  -- JSON blob from Zamplo
    zamplo_gis_data          TEXT,                  -- JSON blob from Zamplo
    zamplo_pulled_at         TEXT,
    in_final_acre_range      INTEGER,               -- 1 if 5-20 acres
    ready_for_mailer         INTEGER DEFAULT 0,
    FOREIGN KEY (filtered_lead_id) REFERENCES leads_filtered (id)
);
CREATE INDEX IF NOT EXISTS idx_enriched_ready ON leads_enriched (ready_for_mailer);
"""


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def get_db_path() -> Path:
    """Resolve DB path from env var or default to data/pipeline.db."""
    env_path = os.getenv("DATABASE_PATH")
    if env_path:
        p = Path(env_path)
        return p if p.is_absolute() else (REPO_ROOT / p)
    return DEFAULT_DB_PATH


def get_conn() -> sqlite3.Connection:
    """Return a connection with row_factory set for dict-like access."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """Context manager that commits on success, rolls back on exception."""
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create all tables. Idempotent — safe to run repeatedly."""
    with transaction() as conn:
        conn.executescript(SCHEMA_SQL)


# ---------------------------------------------------------------------------
# Config loaders
# ---------------------------------------------------------------------------

def load_states_config() -> dict:
    """Load config/states.yaml as a dict keyed by state_code."""
    with open(CONFIG_DIR / "states.yaml") as f:
        return yaml.safe_load(f)


def load_filters_config() -> dict:
    """Load config/filters.yaml."""
    with open(CONFIG_DIR / "filters.yaml") as f:
        return yaml.safe_load(f)


def sync_states_from_config() -> int:
    """Upsert config/states.yaml into the states table. Returns rows touched."""
    cfg = load_states_config()
    rows = 0
    with transaction() as conn:
        for code, data in cfg.items():
            conn.execute(
                """
                INSERT INTO states (state_code, state_name, role_title,
                                    list_typically_free, statute_citation, notes, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(state_code) DO UPDATE SET
                    state_name = excluded.state_name,
                    role_title = excluded.role_title,
                    list_typically_free = excluded.list_typically_free,
                    statute_citation = excluded.statute_citation,
                    notes = excluded.notes,
                    is_active = excluded.is_active,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    code,
                    data["state_name"],
                    data.get("role_title"),
                    1 if data.get("list_typically_free") else 0,
                    data.get("statute_citation"),
                    data.get("notes"),
                    1 if data.get("active") else 0,
                ),
            )
            rows += 1
    return rows
