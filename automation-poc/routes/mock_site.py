"""
Mock target site — simulates the utility portal we will scrape.
Rendered in a deliberately different, plain style to make it obvious
this is a separate site being scraped.

Routes:
  GET  /mock-site/                  Home / landing page
  GET  /mock-site/reports/load      Date-input form (empty)
  POST /mock-site/reports/load      Same page with data table populated
"""
import hashlib
import logging
from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mock-site")
templates = Jinja2Templates(directory="templates")


def _generate_hourly_loads(target_date: date):
    """Deterministic synthetic hourly load data (MW) based on date."""
    hour_factors = [
        0.75, 0.72, 0.70, 0.68, 0.67, 0.70,
        0.78, 0.88, 0.95, 1.00, 1.02, 1.03,
        1.00, 0.97, 0.95, 0.96, 0.98, 1.05,
        1.08, 1.07, 1.03, 0.98, 0.90, 0.82,
    ]
    seed = int(hashlib.md5(target_date.isoformat().encode()).hexdigest()[:8], 16)
    base_load = 1700 + (seed % 300)
    return [
        {"hour": h, "load": round(base_load * hour_factors[h], 1)}
        for h in range(24)
    ]


@router.get("/", response_class=HTMLResponse)
async def mock_home(request: Request):
    return templates.TemplateResponse("mock_site_home.html", {"request": request})


@router.get("/reports/load", response_class=HTMLResponse)
async def mock_load_form(request: Request):
    return templates.TemplateResponse(
        "mock_site_report.html",
        {"request": request, "submitted": False, "report_date": None, "hourly_data": None},
    )


@router.post("/reports/load", response_class=HTMLResponse)
async def mock_load_submit(request: Request, report_date: str = Form(...)):
    target = date.fromisoformat(report_date)
    hourly_data = _generate_hourly_loads(target)
    logger.info("Mock site served %d records for %s", len(hourly_data), target)
    return templates.TemplateResponse(
        "mock_site_report.html",
        {
            "request": request,
            "submitted": True,
            "report_date": report_date,
            "hourly_data": hourly_data,
        },
    )
