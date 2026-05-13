"""
PDF adapter.

Two-pass approach:
    1. Try pdfplumber.extract_tables() for text-based PDFs (~70% of county PDFs).
    2. If no table found OR text is gibberish, fall back to OCR:
       - pdf2image to render each page at ~300 DPI
       - pytesseract.image_to_data(...) for text + bounding boxes
       - reconstruct table structure from x-coordinate clustering
       - OR (if AWS creds present) AWS Textract — much better at table extraction

Tesseract requires `brew install tesseract` and `brew install poppler` on macOS.
"""

from __future__ import annotations

from pathlib import Path


def parse(path: Path) -> list[dict]:
    """
    TODO:
        - attempt pdfplumber first
        - if that returns < 5 rows or table is empty, fall back to OCR path
        - return list[dict] same shape as csv/xlsx adapters
    """
    raise NotImplementedError
