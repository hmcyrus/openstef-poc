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


@router.post("/api/generate-forecast")
async def generate_forecast(
    date: str = Form(...),
    model_names: str = Form(...),  # Comma-separated list of model names
    holiday: int = Form(...),
    holiday_type: int = Form(...),
    nation_event: int = Form(...)
):
    """API endpoint for generating real-time forecasts from current hour to end of day"""
    # Parse the comma-separated model names
    model_names_list = [name.strip() for name in model_names.split(',') if name.strip()]
    
    logger.info(f"Generate Forecast request - Models: {model_names_list}, Date: {date}")
    logger.debug(f"Holiday: {holiday}, Holiday Type: {holiday_type}, Nation Event: {nation_event}")

    try:
        # Get real-time forecast results from multiple models
        forecast_result = await ModelService.generate_realtime_forecast(
            model_names_list, 
            date, 
            holiday, 
            holiday_type, 
            nation_event
        )
        
        logger.info(f"Real-time forecast completed successfully for {len(model_names_list)} models")
        
        return JSONResponse(forecast_result)
    
    except ValueError as e:
        # Handle validation errors (e.g., wrong date, empty model list)
        logger.error(f"Validation error in generate_forecast: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
    
    except FileNotFoundError as e:
        # Handle missing files
        logger.error(f"File not found error in generate_forecast: {str(e)}")
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )
    
    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error in generate_forecast: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected error occurred: {str(e)}"}
        )
