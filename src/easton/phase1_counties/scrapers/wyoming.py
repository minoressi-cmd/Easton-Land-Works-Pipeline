"""
Wyoming county-treasurer scraper.

WY has 23 counties. Each county has a `.gov` site, and the Treasurer is a
constitutional officer with a clearly-labeled contact page in most cases.

Best starting points to find the 23 sites:
- Wyoming Association of County Officers: https://wyocountyofficers.com/
- Wyoming Association of County Treasurers: https://wyocountytreasurers.com/
  (THIS is probably the best single source — they list every Treasurer.)

Strategy:
1. Fetch the WACT (or equivalent) page that lists all Treasurers.
2. For each entry, grab name + email + county name directly from the listing
   if the page exposes them. If not, click through to the county's Treasurer
   page and scrape there.
3. Return a list[CountyContact].
"""

from __future__ import annotations

from easton.phase1_counties.scrapers import CountyContact, StateScraper


WYOMING_COUNTIES = [
    "Albany", "Big Horn", "Campbell", "Carbon", "Converse", "Crook",
    "Fremont", "Goshen", "Hot Springs", "Johnson", "Laramie", "Lincoln",
    "Natrona", "Niobrara", "Park", "Platte", "Sheridan", "Sublette",
    "Sweetwater", "Teton", "Uinta", "Washakie", "Weston",
]


class WyomingScraper(StateScraper):
    state_code = "WY"

    def scrape(self) -> list[CountyContact]:
        """
        TODO:
            - GET the Wyoming County Treasurers Association page
            - parse the directory
            - for each county: build a CountyContact with name + email + phone + website
            - return the list
        """
        raise NotImplementedError(
            "Implement WyomingScraper.scrape() — see docstring for sources."
        )
