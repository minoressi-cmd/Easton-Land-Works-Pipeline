"""
Initialize (or re-initialize) the SQLite database.

Idempotent — running it twice is a no-op. Safe to run after pulling new
schema changes from git.

Usage:
    python scripts/init_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make src/ importable when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from easton.db import init_db, sync_states_from_config, get_db_path


def main() -> None:
    db_path = get_db_path()
    print(f"Initializing DB at: {db_path}")
    init_db()
    print("Schema applied.")
    n = sync_states_from_config()
    print(f"Synced {n} states from config/states.yaml")
    print("Done.")


if __name__ == "__main__":
    main()
