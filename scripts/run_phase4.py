"""
Run Phase 4 — enrich filtered leads via Zamplo, apply final acre filter.

Usage:
    python scripts/run_phase4.py                   # enrich everything pending
    python scripts/run_phase4.py --limit 100       # cap for testing / cost control
    python scripts/run_phase4.py --dry-run         # don't actually call Zamplo
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import click


@click.command()
@click.option("--limit", type=int, default=None)
@click.option("--dry-run", is_flag=True)
def main(limit: int | None, dry_run: bool) -> None:
    # TODO: SELECT FROM leads_filtered LEFT JOIN leads_enriched WHERE enriched is NULL
    #       AND leads_filtered.is_entity = 0 (or trust override per config)
    # For each, call ZamploClient.lookup_by_parcel(), persist into leads_enriched,
    # apply 5-20 acre filter, set ready_for_mailer flag.
    raise NotImplementedError("Implement after Phase 4 client is ready.")


if __name__ == "__main__":
    main()
