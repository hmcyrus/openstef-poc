"""
Scraper service: navigates the target site, submits the date form,
and extracts 24 hourly load readings from the HTML table.

Flow mirrors what will happen against the real utility portal:
  1. GET the report page (grab any hidden form fields / CSRF tokens)
  2. POST the date form
  3. Parse table#load-data from the response HTML
"""
import logging
from datetime import date
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ScraperService:
    REPORT_PATH = "/mock-site/reports/load"

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def scrape_load_data(self, target_date: date) -> List[Dict]:
        """
        Returns a list of 24 dicts: {"hour": int, "load": float}
        """
        url = f"{self.base_url}{self.REPORT_PATH}"

        # Step 1 — GET form page (mirrors navigating to the report menu in a real site)
        logger.info("Step 1/3: Loading report page: %s", url)
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()

        # Step 2 — POST the date (mirrors filling in the date field and submitting)
        logger.info("Step 2/3: Submitting date %s", target_date)
        resp = self.session.post(
            url,
            data={"report_date": target_date.isoformat()},
            timeout=10,
        )
        resp.raise_for_status()

        # Step 3 — Parse table
        logger.info("Step 3/3: Parsing load data table")
        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table", {"id": "load-data"})
        if not table:
            raise ValueError(f"Table #load-data not found in response for {target_date}")

        hourly_data = []
        for row in table.find("tbody").find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                hourly_data.append(
                    {"hour": int(cells[0].text.strip()), "load": float(cells[1].text.strip())}
                )

        logger.info("Extracted %d records for %s", len(hourly_data), target_date)
        return hourly_data
