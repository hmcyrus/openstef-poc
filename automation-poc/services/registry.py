"""
Singleton service instances.
Imported by routes and by main.py — avoids circular imports.
Config is loaded from disk at import time; call refresh() after config changes.
"""
import json
from pathlib import Path

from services.scraper_service import ScraperService
from services.automation_service import AutomationService
from services.scheduler_service import SchedulerService

CONFIG_PATH = Path("config.json")

DEFAULT_CONFIG = {
    "target_url": "http://localhost:8090",
    "run_hour": 6,
    "run_minute": 0,
    "enabled": False,
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


_cfg = load_config()
scraper = ScraperService(base_url=_cfg["target_url"])
automation = AutomationService(scraper=scraper)
scheduler = SchedulerService()
