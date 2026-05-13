"""
Phase 1 — County + tax-collector discovery.

Goal: populate `counties` table with one row per county per active state,
including the email of whoever handles tax-delinquent property lists.

Strategy:
1. `naco_ingest.py` — pull universal county list from NACo (or fallback list)
   to seed `counties` with state + county_name + fips_code only.
2. `scrapers/<state>.py` — per-state scraper that visits each county's official
   site and pulls the contact for the role specified in `config/states.yaml`.
3. `verify.py` — lightweight checks: does the email parse, does the website
   resolve, has it been verified in the last N days.

Build one state at a time. Wyoming first (23 counties — small, mostly free lists).
"""
