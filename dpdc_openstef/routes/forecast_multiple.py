"""Forecast Multiple Models routes"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List
import logging
from services.model_service import ModelService

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/forecast-multiple", response_class=HTMLResponse)
async def forecast_multiple_page(request: Request):
    """Forecast Multiple Models page"""
    return templates.TemplateResponse(
        "forecast_multiple.html", 
        {
            "request": request, 
            "active_page": "forecast-multiple", 
            "available_models": ModelService.get_trained_models()
        }
    )


@router.post("/api/forecast-multiple")
async def forecast_multiple(
    date: str = Form(...),
    model_names: str = Form(...),  # Comma-separated list of model names
    holiday: int = Form(...),
    holiday_type: int = Form(...),
    nation_event: int = Form(...)
):
    """API endpoint for forecasting from multiple models"""
    # Parse the comma-separated model names
    model_names_list = [name.strip() for name in model_names.split(',') if name.strip()]
    
    logger.info(f"Forecast Multiple request - Models: {model_names_list}, Date: {date}")
    logger.debug(f"Holiday: {holiday}, Holiday Type: {holiday_type}, Nation Event: {nation_event}")

    # Get forecast results from multiple models
    forecast_result = await ModelService.forecast_from_mulitple_models(model_names_list, date)
    
    logger.info(f"Forecast completed successfully for {len(model_names_list)} models")
    
    return JSONResponse(forecast_result)
