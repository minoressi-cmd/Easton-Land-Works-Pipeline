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
