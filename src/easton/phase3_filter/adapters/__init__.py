"""
File-format adapters.

Each adapter exposes:

    def parse(path: Path) -> list[dict]:
        '''Return one dict per row, with column names lowercased and stripped.'''

Column normalization is intentionally minimal here — let leads_raw hold the
original keys via raw_data (JSON). Phase 3's normalize_row() in filters.py
maps to the canonical leads_raw columns.

Implement in this order:
    1. csv_adapter.py    (easiest, ~80% of replies)
    2. xlsx_adapter.py   (most of the remaining 20%)
    3. pdf_adapter.py    (text PDFs first; OCR for scanned PDFs comes last)
"""
