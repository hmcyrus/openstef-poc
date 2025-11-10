"""Forecast routes"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import logging
from services.model_service import ModelService

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/forecast", response_class=HTMLResponse)
async def forecast_page(request: Request):
    """Forecast page"""
    return templates.TemplateResponse(
        "forecast.html", 
        {
            "request": request, 
            "active_page": "forecast", 
            "available_models": ModelService.get_trained_models()
        }
    )


@router.post("/api/forecast")
async def forecast(
    date: str = Form(...),
    hour: int = Form(...),
    model_name: str = Form(...),
    holiday: int = Form(...),
    holiday_type: int = Form(...),
    nation_event: int = Form(...),
    weather_data: str = Form(...)
):
    """API endpoint for forecasting"""
    weather_dict = json.loads(weather_data)
    
    logger.info(f"Forecast request - Model: {model_name}, Date: {date}, Hour: {hour}")
    logger.debug(f"Holiday: {holiday}, Holiday Type: {holiday_type}, Nation Event: {nation_event}")
    logger.debug(f"Weather Data: {weather_dict}")

    # Get forecast result from the model service
    forecast_result = await ModelService.forecast_from_model(model_name, date, hour)
    
    logger.info(f"Forecast completed successfully for model: {model_name}")
    
    return JSONResponse(forecast_result)


@router.get("/api/weather")
async def get_weather(date: str, hour: int):
    """API endpoint for fetching weather data"""
    # Mock weather data
    weather_data = {
        "temp": 25.5,
        "rhum": 65.0,
        "prcp": 0.0,
        "wdir": 180.0,
        "wspd": 5.5,
        "pres": 1013.25,
        "cldc": 50.0,
        "coco": 2.0
    }
    
    return JSONResponse(weather_data)


@router.get("/api/forecast-chart")
async def get_forecast_chart(date: str, hour: int):
    """API endpoint for fetching forecast chart data"""
    # Mock chart data - 24 hours of forecasted values
    hours = list(range(24))
    xgb_values = [1200 + i * 10 + (i % 3) * 5 for i in hours]
    lgb_values = [1205 + i * 10 + (i % 4) * 3 for i in hours]
    ensemble_values = [(xgb + lgb) / 2 for xgb, lgb in zip(xgb_values, lgb_values)]
    
    chart_data = {
        "hours": hours,
        "xgboost": xgb_values,
        "lightgbm": lgb_values,
        "ensemble": ensemble_values
    }
    
    return JSONResponse(chart_data)

