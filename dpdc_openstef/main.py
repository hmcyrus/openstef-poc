from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging

# Import routers
from routes import train_model, forecast, forecast_multiple, data_input, dashboard
from utils.logger import setup_logging

# Setup logging once at startup
setup_logging(log_level="INFO", log_file="logs/app.log")

logger = logging.getLogger(__name__)

app = FastAPI(title="DPDC OpenSTEF")


# @app.on_event("startup")
# async def startup_event():
#     """Log application startup"""
#     logger.info("DPDC OpenSTEF application started successfully")


# @app.on_event("shutdown")
# async def shutdown_event():
#     """Log application shutdown"""
#     logger.info("DPDC OpenSTEF application shutting down")


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(train_model.router, tags=["Train Model"])
app.include_router(forecast.router, tags=["Forecast"])
app.include_router(forecast_multiple.router, tags=["Forecast Multiple"])
app.include_router(data_input.router, tags=["Data Input"])
app.include_router(dashboard.router, tags=["Dashboard"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8080)

