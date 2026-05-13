# Architecture

## Pipeline shape

Four phases, each independent, each with its own table(s) in SQLite. Each phase reads
from the previous phase's output table and writes to its own. This means you can re-run
any phase without redoing the work of earlier phases.

```
counties  ──►  outreach_log  ──►  leads_raw  ──►  leads_filtered  ──►  leads_enriched
  (P1)            (P2)              (P3 in)         (P3 out)            (P4)
```

## Why SQLite, not Postgres

- Single file: trivial to back up, trivial to move between Mac Air and Mac Mini.
- No server process: nothing to install, no port to manage.
- Plenty of horsepower for our scale (~3,143 counties total, ~100K leads/year ceiling).
- If we ever outgrow it, the SQL is portable to Postgres with minor changes.

## Why phases instead of one big script

The four phases have different reliability profiles:

- **Phase 1** (scraping) breaks when county sites change layouts.
- **Phase 2** (sending) is rate-limited and async (replies take days/weeks).
- **Phase 3** (parsing) breaks on weird file formats.
- **Phase 4** (Zamplo API) breaks on credit limits, schema changes.

Coupling them would mean one bad scraper kills the whole pipeline. Decoupled, a Phase 1
break still lets Phase 3 process yesterday's inbox.

## Build order

Week 1 — Phase 1, Wyoming only (23 counties, easiest test bed)
Week 2 — Phase 2, sender + records-request template + reply tracking
Week 3 — Phase 3, CSV + XLSX adapters, LLC filter (acres filter waits for Zamplo)
Week 4 — Phase 4, Zamplo API client, end-to-end test
Week 5+ — Add states one at a time: WY → MT → CO → ...

## Key decisions worth surfacing

- **Acre filter happens in Phase 4, not Phase 3.** Many county tax-delinquent lists
  don't include acreage. Zamplo enriches it. So the 5–20 acre cut is the final filter
  before the lead becomes mailer-ready.
- **Entity filter keeps rows, doesn't delete them.** `leads_filtered.is_entity` is a flag.
  Saves us if we ever decide trusts/family LLCs are worth mailing.
- **Every received file is stored.** Even if parsing fails, the raw file goes in
  `data/inbox/` so we can re-parse later with a fixed adapter.
- **Templates live in files, not code.** `phase2_outreach/templates/` so a non-coder can
  edit copy without touching Python.

## What's deliberately NOT here yet

- No web UI. CLI scripts only until the data flow is solid.
- No CRM connector. Zamplo IS the CRM-equivalent for now; we feed it, it owns the rest.
- No skip tracing in the pipeline — Zamplo handles owner enrichment.
- No mailer integration. Mailer logic lives downstream of `leads_enriched`.
