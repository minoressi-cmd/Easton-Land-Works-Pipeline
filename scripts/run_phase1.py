"""
Run Phase 1 for a given state.

Usage:
    python scripts/run_phase1.py --state WY
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import click


@click.command()
@click.option("--state", required=True, help="State code, e.g. WY")
@click.option("--skip-naco", is_flag=True, help="Skip Census/NACo county seeding step")
def main(state: str, skip_naco: bool) -> None:
    state = state.upper()

    if not skip_naco:
        from easton.phase1_counties.naco_ingest import ingest_counties_for_active_states
        print(f"[1/2] Seeding counties for active states ...")
        ingest_counties_for_active_states()

    print(f"[2/2] Scraping contacts for {state} ...")
    if state == "WY":
        from easton.phase1_counties.scrapers.wyoming import WyomingScraper
        scraper = WyomingScraper()
    else:
        raise SystemExit(f"No scraper implemented for {state} yet. Add one in src/easton/phase1_counties/scrapers/")

    contacts = scraper.scrape()
    rows = scraper.upsert(contacts)
    print(f"Upserted {rows} county-contact rows.")


if __name__ == "__main__":
    main()
