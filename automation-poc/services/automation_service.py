"""
Automation service: orchestrates scrape → CSV write.
Both the scheduler and the manual trigger call run_data_collection().
"""
import csv
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

from services.scraper_service import ScraperService

logger = logging.getLogger(__name__)

CSV_PATH = Path("static/data/collected_data.csv")
HEADER = ["date", "hour", "timestamp", "load_mw"]


class AutomationService:
    def __init__(self, scraper: ScraperService):
        self.scraper = scraper
        self._last_run: Dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_data_collection(self, target_date: date) -> Dict:
        """Scrape load data for target_date and persist to CSV."""
        try:
            logger.info("Starting data collection for %s", target_date)
            load_data = self.scraper.scrape_load_data(target_date)
            self._save_to_csv(target_date, load_data)
            result = {
                "date": target_date.isoformat(),
                "status": "success",
                "records": len(load_data),
                "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as exc:
            logger.error("Collection failed for %s: %s", target_date, exc)
            result = {
                "date": target_date.isoformat(),
                "status": "error",
                "error": str(exc),
                "records": 0,
                "run_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        self._last_run = result
        return result

    def run_collection_for_range(self, start: date, end: date) -> List[Dict]:
        results = []
        current = start
        while current <= end:
            results.append(self.run_data_collection(current))
            current += timedelta(days=1)
        return results

    def run_yesterday(self):
        """Entry point called by the scheduler."""
        self.run_data_collection(date.today() - timedelta(days=1))

    @property
    def last_run(self) -> Dict:
        return self._last_run

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _save_to_csv(self, target_date: date, load_data: List[Dict]) -> None:
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Read all existing rows except for this date (so we can overwrite)
        existing: List[Dict] = []
        if CSV_PATH.exists():
            with open(CSV_PATH, newline="") as f:
                for row in csv.DictReader(f):
                    if row["date"] != target_date.isoformat():
                        existing.append(row)

        # Build new rows
        new_rows = [
            {
                "date": target_date.isoformat(),
                "hour": item["hour"],
                "timestamp": datetime(
                    target_date.year, target_date.month, target_date.day, item["hour"]
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "load_mw": item["load"],
            }
            for item in load_data
        ]

        all_rows = existing + new_rows
        all_rows.sort(key=lambda r: (r["date"], int(r["hour"])))

        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(all_rows)

        logger.info("Saved %d rows for %s to %s", len(new_rows), target_date, CSV_PATH)
