"""
Colorado county-treasurer scraper.

CO has 64 counties. Each county elects a County Treasurer.

Primary sources:
- Colorado County Treasurers' Association: https://coloradotreasurers.org/
- Colorado DOLA (Dept of Local Affairs) county directory: https://dola.colorado.gov/
- Individual county .gov sites as fallback

Strategy:
1. Pull county list + FIPS from US Census national county file.
2. Scrape CCTA member directory for name/email/phone.
3. Return a list[CountyContact] merging both.
"""

from __future__ import annotations

import csv
import io
import logging
import re

import requests
from bs4 import BeautifulSoup

from easton.phase1_counties.scrapers import CountyContact, StateScraper

log = logging.getLogger(__name__)

CENSUS_COUNTY_URL = (
    "https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt"
)
CCTA_URL = "https://cctpta.org/"
CCTA_MEMBERS_URL = "https://cctpta.org/member-roster/"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _fetch_co_counties_from_census() -> list[dict]:
    """Download Census FIPS file and return CO rows as list of dicts."""
    log.info("Fetching Census county FIPS file …")
    resp = requests.get(CENSUS_COUNTY_URL, headers=_HEADERS, timeout=30)
    resp.raise_for_status()
    rows = []
    reader = csv.reader(io.StringIO(resp.text))
    for row in reader:
        if len(row) < 4:
            continue
        state, statefp, countyfp, county_name = row[0], row[1], row[2], row[3]
        if state.strip() == "CO":
            fips = statefp.strip() + countyfp.strip()
            rows.append({"county_name": county_name.strip(), "fips": fips})
    log.info("Found %d Colorado counties in Census file.", len(rows))
    return rows


def _scrape_ccta(session: requests.Session) -> dict[str, dict]:
    """
    Scrape the Colorado County Treasurers' Association site.

    Returns a dict keyed by normalized county name with sub-keys:
    name, email, phone, website.
    """
    contacts: dict[str, dict] = {}

    for url in (CCTA_MEMBERS_URL, CCTA_URL):
        try:
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as exc:
            log.warning("Could not fetch %s: %s", url, exc)
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        # Common patterns on member-directory pages:
        # - <a href="mailto:..."> for email
        # - text nodes like "Adams County" near a name block
        # Try to find repeating blocks that look like member cards
        email_pattern = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
        phone_pattern = re.compile(r"\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}")

        # Extract all email links; try to find surrounding county name text
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href.startswith("mailto:"):
                continue
            email = href.replace("mailto:", "").strip().lower()
            # Walk up to find a block that might contain a county name
            parent = a_tag.parent
            for _ in range(5):
                if parent is None:
                    break
                text = parent.get_text(" ", strip=True)
                # Look for "XYZ County" in the text block
                county_match = re.search(r"([A-Z][a-z ]+ County)", text)
                if county_match:
                    county_raw = county_match.group(1)
                    key = _normalize(county_raw)
                    if key not in contacts:
                        contacts[key] = {}
                    contacts[key]["email"] = email
                    # Try to find a name — often the text before "County Treasurer"
                    name_match = re.search(
                        r"([A-Z][a-z]+(?: [A-Z][a-z]+)+)\s*(?:County Treasurer|Treasurer)",
                        text,
                    )
                    if name_match:
                        contacts[key]["name"] = name_match.group(1)
                    # Phone
                    phone_match = phone_pattern.search(text)
                    if phone_match:
                        contacts[key]["phone"] = phone_match.group(0)
                    break
                parent = parent.parent

        if contacts:
            log.info("Found %d contact entries on %s", len(contacts), url)
            break

    return contacts


def _normalize(name: str) -> str:
    """Lowercase, strip ' County' suffix, strip whitespace."""
    return re.sub(r"\s+county\s*$", "", name.strip().lower())


class ColoradoScraper(StateScraper):
    state_code = "CO"

    def scrape(self) -> list[CountyContact]:
        session = requests.Session()
        session.headers.update(_HEADERS)

        counties = _fetch_co_counties_from_census()
        ccta = _scrape_ccta(session)

        contacts = []
        for c in counties:
            key = _normalize(c["county_name"])
            info = ccta.get(key, {})
            contacts.append(
                CountyContact(
                    state_code="CO",
                    county_name=c["county_name"],
                    contact_name=info.get("name"),
                    contact_email=info.get("email"),
                    contact_phone=info.get("phone"),
                    office_website=info.get("website"),
                    list_format_known="unknown",
                    list_cost_cents=None,   # CO often charges; amount varies
                    list_request_method="email",
                    notes=f"FIPS: {c['fips']}",
                )
            )

        log.info(
            "Returning %d CO county contacts (%d with email from CCTA).",
            len(contacts),
            sum(1 for ct in contacts if ct.contact_email),
        )
        return contacts
