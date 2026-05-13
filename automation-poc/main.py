import json
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import services.registry as reg
from routes import data_collection, mock_site

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("static/data", exist_ok=True)
    cfg = reg.load_config()
    reg.scheduler.start()
    reg.scheduler.reschedule(
        cfg["run_hour"],
        cfg["run_minute"],
        reg.automation.run_yesterday,
        cfg["enabled"],
    )
    logger.info("Automation POC started — mock site at /mock-site/, UI at /")
    yield
    reg.scheduler.stop()
    logger.info("Automation POC stopped")


app = FastAPI(title="Data Collection Automation POC", lifespan=lifespan)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(mock_site.router, tags=["Mock Target Site"])
app.include_router(data_collection.router, tags=["Data Collection"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090, reload=False)
