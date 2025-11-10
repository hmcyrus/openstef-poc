"""Data Input routes"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/data-input", response_class=HTMLResponse)
async def data_input_page(request: Request):
    """Data Input page"""
    return templates.TemplateResponse("data_input.html", {"request": request, "active_page": "data_input"})


@router.get("/api/data-input")
async def get_data_input(date: str):
    """API endpoint for fetching predicted and actual data for a specific date"""
    logger.info(f"Fetching data input for date: {date}")
    
    # Mock data - 24 hours of predicted and actual values
    hourly_data = []
    for hour in range(24):
        hourly_data.append({
            "hour": hour,
            "predicted": 1200 + hour * 10 if hour % 2 == 0 else 0,
            "actual": 1195 + hour * 10 if hour % 3 == 0 else 0
        })
    
    logger.debug(f"Retrieved {len(hourly_data)} hourly records for date: {date}")
    
    return JSONResponse({"date": date, "data": hourly_data})


@router.post("/api/data-input")
async def update_data_input(
    date: str = Form(...),
    hourly_data: str = Form(...)
):
    """API endpoint for updating predicted and actual data"""
    data_list = json.loads(hourly_data)
    
    logger.info(f"Updating data for date: {date} with {len(data_list)} records")
    logger.debug(f"Hourly data: {data_list}")
    
    logger.info(f"Data updated successfully for {date}")
    
    return JSONResponse({
        "status": "success",
        "message": f"Data updated successfully for {date}",
        "records_updated": len(data_list)
    })

