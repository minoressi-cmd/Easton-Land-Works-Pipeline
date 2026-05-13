"""
Base class for per-state county-contact scrapers.

Subclass this for each state. Each subclass knows:
- where the state's county-government directory lives
- how to locate the right office for that state's role_title
- how to extract the email (and ideally name + phone)

Don't try to make this generic across all 50 states. State sites vary too much.
One subclass per state is fine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CountyContact:
    """One county's contact info for the tax-delinquent records request."""
    state_code: str
    county_name: str
    contact_name: str | None
    contact_email: str | None
    contact_phone: str | None
    office_website: str | None
    list_format_known: str = "unknown"     # csv | xlsx | pdf | unknown
    list_cost_cents: int | None = None     # 0 if confirmed free
    list_request_method: str = "email"     # email | form | foia | phone
    notes: str | None = None


class StateScraper(ABC):
    """Base class. One subclass per state."""

    state_code: str = ""

    @abstractmethod
    def scrape(self) -> list[CountyContact]:
        """Return contacts for every county in the state."""
        ...

    def upsert(self, contacts: list[CountyContact]) -> int:
        """Write contacts into the counties table. Returns rows touched."""
        from easton.db import transaction
        rows = 0
        with transaction() as conn:
            for c in contacts:
                conn.execute(
                    """
                    UPDATE counties
                       SET contact_name = ?,
                           contact_email = ?,
                           contact_phone = ?,
                           office_website = ?,
                           list_format_known = ?,
                           list_cost_cents = ?,
                           list_request_method = ?,
                           notes = COALESCE(?, notes),
                           last_verified = DATE('now'),
                           updated_at = CURRENT_TIMESTAMP
                     WHERE state_code = ? AND county_name = ?
                    """,
                    (
                        c.contact_name,
                        c.contact_email,
                        c.contact_phone,
                        c.office_website,
                        c.list_format_known,
                        c.list_cost_cents,
                        c.list_request_method,
                        c.notes,
                        c.state_code,
                        c.county_name,
                    ),
                )
                rows += conn.total_changes
        return rows
