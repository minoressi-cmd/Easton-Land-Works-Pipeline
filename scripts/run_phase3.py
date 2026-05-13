"""
Run Phase 3 — parse + filter sheets received in data/inbox/.

Usage:
    python scripts/run_phase3.py                   # process everything new
    python scripts/run_phase3.py --county-id 17    # one county only
    python scripts/run_phase3.py --reparse         # re-parse already-imported files
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import click


@click.command()
@click.option("--county-id", type=int, default=None)
@click.option("--reparse", is_flag=True)
def main(county_id: int | None, reparse: bool) -> None:
    # TODO: SELECT outreach_log WHERE status = 'list_received' AND attachment_path IS NOT NULL
    # For each, dispatch to the right adapter by file extension, normalize, insert into leads_raw,
    # then run the entity filter and insert leads_filtered.
    raise NotImplementedError("Implement after Phase 3 adapters are done.")


if __name__ == "__main__":
    main()
