"""
Build a CSV of all 64 Colorado counties and their County Treasurers.

Usage:
    python scripts/export_colorado_treasurers.py
    python scripts/export_colorado_treasurers.py --out data/colorado_treasurers.csv

Steps:
1. Scrape county list from Census FIPS + CCTA for contacts.
2. Write to CSV (and optionally upsert into pipeline.db).
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import click
from rich.console import Console
from rich.table import Table

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
console = Console()

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "data" / "colorado_treasurers.csv"

CSV_FIELDS = [
    "county_name",
    "fips_code",
    "state",
    "role_title",
    "contact_name",
    "contact_email",
    "contact_phone",
    "office_website",
    "list_request_method",
    "notes",
]


@click.command()
@click.option(
    "--out",
    default=str(DEFAULT_OUT),
    show_default=True,
    help="Output CSV path.",
)
@click.option(
    "--save-db",
    is_flag=True,
    default=False,
    help="Also upsert results into pipeline.db counties table.",
)
def main(out: str, save_db: bool) -> None:
    from easton.phase1_counties.scrapers.colorado import ColoradoScraper

    console.rule("[bold]Colorado Treasurer Export[/bold]")
    scraper = ColoradoScraper()

    console.print("Fetching counties from Census FIPS + CCTA …")
    contacts = scraper.scrape()

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for c in contacts:
            fips = ""
            if c.notes and c.notes.startswith("FIPS:"):
                fips = c.notes.split("FIPS:")[-1].strip()
            writer.writerow({
                "county_name": c.county_name,
                "fips_code": fips,
                "state": "CO",
                "role_title": "County Treasurer",
                "contact_name": c.contact_name or "",
                "contact_email": c.contact_email or "",
                "contact_phone": c.contact_phone or "",
                "office_website": c.office_website or "",
                "list_request_method": c.list_request_method,
                "notes": "",
            })

    console.print(f"\n[green]Wrote {len(contacts)} rows → {out_path}[/green]")

    # Summary table
    table = Table(title="Colorado County Treasurers", show_lines=False)
    table.add_column("County", style="cyan")
    table.add_column("FIPS")
    table.add_column("Treasurer Name")
    table.add_column("Email")
    table.add_column("Phone")

    for c in sorted(contacts, key=lambda x: x.county_name):
        fips = c.notes.split("FIPS:")[-1].strip() if c.notes else ""
        table.add_row(
            c.county_name,
            fips,
            c.contact_name or "—",
            c.contact_email or "—",
            c.contact_phone or "—",
        )
    console.print(table)

    if save_db:
        console.print("Upserting into pipeline.db …")
        rows = scraper.upsert(contacts)
        console.print(f"[green]Upserted {rows} rows.[/green]")


if __name__ == "__main__":
    main()
