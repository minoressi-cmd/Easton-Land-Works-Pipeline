"""
Run Phase 2 — send records requests for counties that haven't been emailed yet.

Usage:
    python scripts/run_phase2.py --state WY --dry-run
    python scripts/run_phase2.py --state WY                  # send for real
    python scripts/run_phase2.py --state WY --limit 10       # cap this run
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import click


@click.command()
@click.option("--state", required=True)
@click.option("--dry-run/--no-dry-run", default=True)
@click.option("--limit", type=int, default=None)
def main(state: str, dry_run: bool, limit: int | None) -> None:
    # TODO: select counties WHERE state=? AND contact_email IS NOT NULL
    #       AND id NOT IN (SELECT county_id FROM outreach_log WHERE status != 'bounced')
    # call send_records_request for each, respecting EMAIL_DAILY_CAP and --limit
    raise NotImplementedError("Implement when Phase 2 sender is ready.")


if __name__ == "__main__":
    main()
