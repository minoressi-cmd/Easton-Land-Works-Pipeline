"""CSV adapter — pandas-based, handles UTF-8 / latin-1 / weird delimiters."""

from __future__ import annotations

from pathlib import Path


def parse(path: Path) -> list[dict]:
    """
    TODO:
        - try pd.read_csv with utf-8, fall back to latin-1
        - detect delimiter via csv.Sniffer
        - lowercase + strip column names
        - return df.to_dict(orient='records')
    """
    raise NotImplementedError
