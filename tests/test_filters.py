"""Tests for the entity-classifier — this one works today, no stubs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from easton.phase3_filter.filters import classify_entity


def test_individual_name():
    is_entity, _ = classify_entity("John Q Public")
    assert is_entity is False


def test_basic_llc():
    is_entity, pat = classify_entity("Smith Family LLC")
    assert is_entity is True
    assert pat == "LLC"


def test_punctuated_llc():
    is_entity, pat = classify_entity("Smith Family, L.L.C.")
    assert is_entity is True


def test_corp():
    is_entity, pat = classify_entity("ACME CORPORATION")
    assert is_entity is True


def test_trust():
    is_entity, pat = classify_entity("Jones Family Trust")
    assert is_entity is True
    assert pat == "TRUST"


def test_empty():
    is_entity, _ = classify_entity("")
    assert is_entity is False


def test_none():
    is_entity, _ = classify_entity(None)
    assert is_entity is False


def test_word_boundary_not_substring():
    # "Linc" shouldn't match "INC"
    is_entity, _ = classify_entity("Lincoln Smith")
    assert is_entity is False
