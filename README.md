# Easton Land Works — Lead Pipeline

End-to-end pipeline for sourcing tax-delinquent land leads:

```
[Phase 1] Build county directory  →  who do we email, in which state, for what?
[Phase 2] Send records requests   →  ask each county for their tax-delinquent list
[Phase 3] Parse + filter sheets   →  drop entities, normalize, prep for enrichment
[Phase 4] Push to Zamplo          →  enrich via API, pull back parcel/owner/value data
```

Target acre range: **5–20 acres** (Easton Land Works standard).

---

## What it does

### Phase 1 — County Discovery

Builds a database of every county contact (Treasurer, Tax Collector, etc.) in each active state. Targets Wyoming's 23 counties first as the initial test bed. The scraper hits the Wyoming County Treasurers Association site to pull contact names, emails, and phone numbers. A US Census FIPS file seeds the county list with all ~3,143 counties nationally.

State-level config lives in `config/states.yaml`. Wyoming (`WY`) is currently active; Montana, Colorado, Texas, Florida, Georgia, Tennessee, and Mississippi are staged but inactive. Each entry records the correct role title for that state's tax official and the public records statute to cite in the request.

### Phase 2 — Records Requests

Emails each county treasurer (or equivalent) asking for their tax-delinquent parcel list. Uses Postmark for delivery and enforces a daily send cap (`EMAIL_DAILY_CAP` in `.env`) to avoid triggering spam filters. Every send is logged to the `outreach_log` table, which tracks status through: `sent → replied → attachment received`. Email templates live in plain-text files under `phase2_outreach/templates/` so copy can be edited without touching Python.

### Phase 3 — Parse & Filter

Handles whatever file format the county sends back — CSV, XLSX, or PDF. Each format has its own adapter that normalizes the raw rows into a canonical schema before writing to `leads_raw`.

After parsing, rows go through two filters:

- **Entity filter:** flags LLC, Corp, Trust, and similar owner-name patterns (defined in `config/filters.yaml`). Entities are flagged with `is_entity = 1` but **not deleted** — they remain in `leads_filtered` so Easton can mail trusts or family LLCs later if the strategy changes.
- **Delinquency floor:** drops parcels with less than `min_delinquent_amount_usd` owed (default $50) to skip trivial liens not worth mailing.

### Phase 4 — Zamplo Enrichment

Pushes filtered leads to the Zamplo property data API to pull back acreage, estimated value, owner details, and GIS data. The **5–20 acre filter is applied here**, not in Phase 3, because most county tax-delinquent lists do not include acreage. Leads that survive this final cut come out as `ready_for_mailer = 1` in `leads_enriched`.

### Data store

Single SQLite file at `data/pipeline.db`. Each phase reads from the previous phase's output table and writes to its own, so any phase can be re-run independently without redoing earlier work:

```
counties → outreach_log → leads_raw → leads_filtered → leads_enriched
  (P1)          (P2)         (P3 in)      (P3 out)          (P4)
```

### What's implemented vs. stubbed

| Component | Status |
|---|---|
| SQLite schema + connection helpers | Done |
| Config loaders (states, filters) | Done |
| Entity-pattern classifier (`classify_entity`) | Done |
| Census FIPS county ingest | Stub |
| Wyoming scraper | Stub |
| Email sender (Postmark) | Stub |
| CSV / XLSX / PDF adapters | Stub |
| Row normalizer | Stub |
| Zamplo API client | Stub |

---

## Quick start

```bash
# 1. Clone
git clone <repo-url> easton-pipeline
cd easton-pipeline

# 2. Python env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Secrets
cp .env.example .env
# Edit .env with real API keys

# 4. Initialize the database
python scripts/init_db.py

# 5. Run a phase (start with Phase 1, Wyoming)
python scripts/run_phase1.py --state WY
```

---

## Where things live

| Path | What's in it |
|---|---|
| `src/easton/db.py` | SQLite schema + connection helper. Source of truth for all tables. |
| `src/easton/phase1_counties/` | County + contact discovery. State-by-state scrapers. |
| `src/easton/phase2_outreach/` | Email sender, templates, reply tracking. |
| `src/easton/phase3_filter/` | File adapters (csv/xlsx/pdf) + filter rules. |
| `src/easton/phase4_zamplo/` | Zamplo API client + enrichment workflow. |
| `config/states.yaml` | Per-state config: role title, statute citation, list cost. |
| `config/filters.yaml` | Entity-name patterns, acre range thresholds. |
| `data/pipeline.db` | SQLite database (gitignored). |
| `data/inbox/` | Received county sheets (gitignored). |
| `docs/HANDOFF.md` | **Read this first when moving to the Mac Mini.** |
| `docs/ARCHITECTURE.md` | Why the pipeline is shaped this way. |
| `docs/DECISIONS.md` | Running log of decisions + tradeoffs. |
| `scripts/run_phase*.py` | Entry points for each phase. |

---

## Status

Scaffolding only — no phase is implemented yet. Build order in `docs/ARCHITECTURE.md`.
