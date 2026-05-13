"""
Data Collection UI routes.

GET  /                        Main page
POST /api/config              Save config + reschedule
POST /api/collection/run      Manual trigger for a date range
GET  /api/status              JSON status (scheduler + last run)
"""
import csv
import logging
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import services.registry as reg

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CSV_PATH = Path("static/data/collected_data.csv")


def _data_preview(n: int = 48):
    if not CSV_PATH.exists():
        return []
    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    return list(reversed(rows[-n:]))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cfg = reg.load_config()
    return templates.TemplateResponse(
        "data_collection.html",
        {
            "request": request,
            "active_page": "data_collection",
            "config": cfg,
            "scheduler_running": reg.scheduler.is_running,
            "job_active": reg.scheduler.job_exists(),
            "next_run": reg.scheduler.get_next_run(),
            "last_run": reg.automation.last_run,
            "data_preview": _data_preview(),
        },
    )


@router.post("/api/config")
async def update_config(
    target_url: str = Form(...),
    run_hour: int = Form(...),
    run_minute: int = Form(...),
    enabled: str = Form("off"),
):
    cfg = {
        "target_url": target_url.rstrip("/"),
        "run_hour": run_hour,
        "run_minute": run_minute,
        "enabled": enabled == "on",
    }
    reg.save_config(cfg)
    reg.scraper.base_url = cfg["target_url"]
    reg.scheduler.reschedule(run_hour, run_minute, reg.automation.run_yesterday, cfg["enabled"])
    return JSONResponse({"status": "ok", "message": "Configuration saved."})


@router.post("/api/collection/run")
async def run_manual(
    start_date: str = Form(...),
    end_date: str = Form(...),
):
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if start > end:
        return JSONResponse({"status": "error", "message": "start_date must be ≤ end_date"}, status_code=400)
    if (end - start).days >= 30:
        return JSONResponse({"status": "error", "message": "Date range cannot exceed 30 days"}, status_code=400)

    results = reg.automation.run_collection_for_range(start, end)
    return JSONResponse(
        {
            "status": "ok",
            "results": results,
            "total": len(results),
            "success_count": sum(1 for r in results if r["status"] == "success"),
            "error_count": sum(1 for r in results if r["status"] == "error"),
        }
    )


@router.get("/api/status")
async def get_status():
    cfg = reg.load_config()
    return JSONResponse(
        {
            "scheduler_running": reg.scheduler.is_running,
            "job_active": reg.scheduler.job_exists(),
            "next_run": reg.scheduler.get_next_run(),
            "last_run": reg.automation.last_run,
            "config": cfg,
        }
    )
