"""Backtesting routes"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
from services.model_service import ModelService

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/backtesting", response_class=HTMLResponse)
async def backtesting_page(request: Request):
    """Render the backtesting page."""
    return templates.TemplateResponse(
        "backtesting.html",
        {
            "request": request,
            "active_page": "backtesting",
            "available_models": ModelService.get_trained_models()
        },
    )


@router.post("/api/forecast-multiple")
async def forecast_multiple(
    date: str = Form(...),
    model_names: str = Form(...),  # Comma-separated list of model names
):
    """API endpoint for forecasting from multiple models (backtesting)."""
    model_names_list = [name.strip() for name in model_names.split(',') if name.strip()]

    logger.info(f"Forecast Multiple request - Models: {model_names_list}, Date: {date}")

    forecast_result = await ModelService.forecast_from_mulitple_models(model_names_list, date)

    logger.info(f"Forecast completed successfully for {len(model_names_list)} models")

    return JSONResponse(forecast_result)


