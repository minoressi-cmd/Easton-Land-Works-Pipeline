"""
Seed the counties table with the universal county list.

We need a row for every county in every active state BEFORE the per-state
scraper runs (the scraper fills in contact details for existing rows).

Sources (in preference order):
1. NACo county directory — https://www.naco.org/counties (web scrape or use their data files)
2. US Census FIPS list — https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt
   This is the most reliable nationwide list. Plain text. ~3,143 rows.

Recommended: start with the Census FIPS file. Format:
    STATE,STATEFP,COUNTYFP,COUNTYNAME,CLASSFP
    AL,01,001,Autauga County,H1

Stub below. Implement when starting Phase 1.
"""

from __future__ import annotations

import logging

from easton.db import transaction, load_states_config

log = logging.getLogger(__name__)


CENSUS_COUNTY_FILE_URL = (
    "https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt"
)


def ingest_counties_for_active_states() -> int:
    """
    Download the Census county list, filter to active states, upsert into
    `counties`. Returns the number of rows touched.

    TODO:
        - fetch CENSUS_COUNTY_FILE_URL
        - parse CSV
        - filter to states where states.is_active = 1
        - upsert into counties(state_code, county_name, fips_code)
    """
    raise NotImplementedError("Implement when starting Phase 1 — see docstring.")
