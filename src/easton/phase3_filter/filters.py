"""
Filter logic for Phase 3.

Includes a working entity-pattern matcher (the rest is stubs).
"""

from __future__ import annotations

import re

from easton.db import load_filters_config


def _build_entity_regex() -> re.Pattern:
    """Compile the entity-pattern list from filters.yaml into one regex."""
    cfg = load_filters_config()
    patterns = cfg.get("entity_patterns", [])
    # Escape each pattern, allow surrounding word boundaries OR punctuation
    escaped = [re.escape(p) for p in patterns]
    joined = "|".join(escaped)
    # Match as a whole token (preceded by start/space/punct, followed by end/space/punct)
    return re.compile(rf"(?:^|[\s,.;:()])({joined})(?:$|[\s,.;:()])", re.IGNORECASE)


_ENTITY_RE = _build_entity_regex()


def classify_entity(owner_name: str | None) -> tuple[bool, str | None]:
    """
    Return (is_entity, matched_pattern_or_None).

    >>> classify_entity("Smith Family LLC")
    (True, 'LLC')
    >>> classify_entity("John Q Public")
    (False, None)
    >>> classify_entity("Acme Holdings, Inc.")
    (True, 'HOLDINGS')   # first match wins
    """
    if not owner_name:
        return False, None
    m = _ENTITY_RE.search(owner_name)
    if m:
        return True, m.group(1).upper()
    return False, None


def normalize_row(raw: dict) -> dict:
    """
    Map a parsed row dict to the canonical leads_raw column names.

    Strategy: fuzzy-match common header variants. County sheets call the
    owner column "OWNER", "Owner Name", "Taxpayer", "Name of Record", etc.

    TODO: build the mapping table from real examples as you parse first sheets.
    Hardcoding it premature; let real data drive it.
    """
    raise NotImplementedError("Implement after seeing first 3 real county sheets.")
