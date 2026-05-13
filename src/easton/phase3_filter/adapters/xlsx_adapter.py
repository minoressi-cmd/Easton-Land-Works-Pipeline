"""XLSX adapter — handles multi-sheet workbooks, header rows that aren't row 0."""

from __future__ import annotations

from pathlib import Path


def parse(path: Path) -> list[dict]:
    """
    TODO:
        - openpyxl/pd.read_excel
        - if multiple sheets, prefer the one whose name matches /delinquent|tax sale|parcels/i
        - some counties put a 1-3 row preamble before the headers — auto-detect by
          looking for the first row where >=3 cells are non-empty and look like headers
        - normalize column names like csv_adapter
    """
    raise NotImplementedError
