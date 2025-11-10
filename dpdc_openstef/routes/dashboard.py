"""Dashboard routes"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})


@router.get("/api/dashboard-data")
async def get_dashboard_data():
    """API endpoint for fetching dashboard data"""
    logger.info("Fetching dashboard data")
    
    # Mock dashboard data
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", 
             "2024-01-06", "2024-01-07"]
    
    dashboard_data = {
        "daily_forecast": {
            "dates": dates,
            "actual": [1200, 1250, 1180, 1300, 1280, 1220, 1260],
            "predicted": [1210, 1240, 1190, 1290, 1275, 1230, 1255]
        },
        "model_performance": {
            "models": ["XGBoost", "LightGBM", "Ensemble"],
            "mae": [45.2, 48.5, 42.1],
            "rmse": [58.3, 61.2, 55.7],
            "r2": [0.92, 0.91, 0.94]
        },
        "hourly_pattern": {
            "hours": list(range(24)),
            "avg_load": [900, 850, 820, 800, 810, 850, 950, 1100, 1250, 1350, 1400, 1420,
                        1400, 1380, 1350, 1320, 1300, 1350, 1400, 1380, 1300, 1200, 1100, 1000]
        }
    }
    
    logger.debug("Dashboard data retrieved successfully")
    
    return JSONResponse(dashboard_data)

