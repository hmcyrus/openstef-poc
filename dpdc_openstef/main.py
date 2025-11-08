from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

app = FastAPI(title="DPDC OpenSTEF")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


# ==================== Train Model Routes ====================
@app.get("/", response_class=HTMLResponse)
async def train_model_page(request: Request):
    """Train Model page"""
    return templates.TemplateResponse("train_model.html", {"request": request, "active_page": "train"})


@app.post("/api/train")
async def train_model(
    model: str = Form(...),
    hyperparams: str = Form(...)
):
    """API endpoint for training model"""
    hyperparams_dict = json.loads(hyperparams)
    print(f"Model: {model}")
    print(f"Hyperparameters: {hyperparams_dict}")
    
    return JSONResponse({
        "status": "success",
        "message": f"Training initiated for {model} model",
        "model": model,
        "hyperparameters": hyperparams_dict
    })


# ==================== Forecast Routes ====================
@app.get("/forecast", response_class=HTMLResponse)
async def forecast_page(request: Request):
    """Forecast page"""
    return templates.TemplateResponse("forecast.html", {"request": request, "active_page": "forecast"})


@app.post("/api/forecast")
async def forecast(
    date: str = Form(...),
    hour: int = Form(...),
    holiday: int = Form(...),
    holiday_type: int = Form(...),
    nation_event: int = Form(...),
    weather_data: str = Form(...)
):
    """API endpoint for forecasting"""
    weather_dict = json.loads(weather_data)
    
    print(f"Forecast request - Date: {date}, Hour: {hour}")
    print(f"Holiday: {holiday}, Holiday Type: {holiday_type}, Nation Event: {nation_event}")
    print(f"Weather Data: {weather_dict}")
    
    # Mock forecast response
    forecast_results = [
        {"model_name": "XGBoost", "forecasted_value": 1234.56},
        {"model_name": "LightGBM", "forecasted_value": 1245.78},
        {"model_name": "Ensemble", "forecasted_value": 1240.17}
    ]
    
    return JSONResponse(forecast_results)


@app.get("/api/weather")
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


@app.get("/api/forecast-chart")
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


# ==================== Data Input Routes ====================
@app.get("/data-input", response_class=HTMLResponse)
async def data_input_page(request: Request):
    """Data Input page"""
    return templates.TemplateResponse("data_input.html", {"request": request, "active_page": "data_input"})


@app.get("/api/data-input")
async def get_data_input(date: str):
    """API endpoint for fetching predicted and actual data for a specific date"""
    # Mock data - 24 hours of predicted and actual values
    hourly_data = []
    for hour in range(24):
        hourly_data.append({
            "hour": hour,
            "predicted": 1200 + hour * 10 if hour % 2 == 0 else 0,
            "actual": 1195 + hour * 10 if hour % 3 == 0 else 0
        })
    
    return JSONResponse({"date": date, "data": hourly_data})


@app.post("/api/data-input")
async def update_data_input(
    date: str = Form(...),
    hourly_data: str = Form(...)
):
    """API endpoint for updating predicted and actual data"""
    data_list = json.loads(hourly_data)
    
    print(f"Updating data for date: {date}")
    print(f"Hourly data: {data_list}")
    
    return JSONResponse({
        "status": "success",
        "message": f"Data updated successfully for {date}",
        "records_updated": len(data_list)
    })


# ==================== Dashboard Routes ====================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})


@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """API endpoint for fetching dashboard data"""
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
    
    return JSONResponse(dashboard_data)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, port=8080)

