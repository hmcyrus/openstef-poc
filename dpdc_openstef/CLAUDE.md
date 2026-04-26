# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

All commands must be run from inside `dpdc_openstef/`.

```bash
# Install dependencies (Poetry)
poetry install

# Start the server (hot-reload)
poetry run uvicorn main:app --reload --host 127.0.0.1 --port 8080

# Or simply
poetry run python main.py
```

Via Docker:
```bash
docker compose up --build
```

Log level and file path are controlled by environment variables:
```bash
LOG_LEVEL=DEBUG LOG_FILE=logs/app.log poetry run uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

Set `LOG_FILE=` (empty) to disable file logging.

## Architecture Overview

This is a **FastAPI** web application for electrical load forecasting in Dhaka, Bangladesh. It wraps the **OpenSTEF** ML library (`openstef==3.4.72`) to train models and generate demand forecasts.

### Request Flow

```
Browser → routes/*.py (FastAPI router) → services/model_service.py → OpenSTEF pipelines
                                        → services/weather_service.py (Meteostat API)
                                        → static/master_data_with_forecasted.csv (source of truth)
```

### Key Architectural Decisions

**`static/master_data_with_forecasted.csv` is the single source of truth.** All training, forecasting, and the dashboard read from this file. The Data Input page writes back to it (with `.csv.bak` as a safety backup). The CSV schema is:
```
date_time, load, is_holiday, holiday_type, national_event_type, temp, dwpt, rhum, prcp, wdir, wspd, pres, coco, forecasted_load
```
Timestamps in the CSV are stored in **Dhaka timezone (UTC+6)**. OpenSTEF returns forecasts in **UTC**, so `model_service.py` handles conversion when matching forecast results back to Dhaka hours.

**Trained models are persisted as MLflow artifacts** under `trained_models/<custom_name>/`:
- `pj.pkl` — pickled `PredictionJobDataClass` (required to run forecasts)
- `training_metadata.json` — training config snapshot
- `training_data.csv` — copy of the CSV used for training
- `mlflow_trained_models/` — MLflow tracking URI used by OpenSTEF
- `mlflow_artifacts/` — MLflow artifacts folder

**Two forecasting modes:**
1. **Backtesting** (`/backtesting` → `POST /api/forecast-multiple`): runs `ModelService.forecast_from_mulitple_models()` for any historical date already in the CSV.
2. **Real-time** (`/forecast-multiple` → `POST /api/generate-forecast`): runs `ModelService.generate_realtime_forecast()`, which validates the date is today (Dhaka time), reads historical hours from the CSV, fetches weather for missing future hours from Meteostat, then generates forecasts from the current hour to 23.

**`forecast.py` and its route are currently disabled** — `main.py` comments out the import and `app.include_router` call.

### Modules

- `main.py` — app factory, mounts `/static`, registers routers, creates `trained_models/` on startup
- `routes/` — thin HTTP handlers; each file owns one page and its API endpoints
- `services/model_service.py` — all OpenSTEF interactions: `train_model_pipeline`, `create_forecast_pipeline`, helper functions for index lookups and data prep
- `services/weather_service.py` — singleton `WeatherService` wrapping Meteostat `Hourly`; hardcoded to Dhaka coordinates (23.8103°N, 90.4125°E)
- `services/dropdown_service.py` — loads holiday/event code CSVs from `static/config/`
- `utils/dateutils.py` — `create_utc_datetime(date_str, hour, tz)` used throughout for consistent timestamp creation
- `utils/logger.py` — `setup_logging()` called twice (import time + lifespan) to survive uvicorn's log config override; weekly rotating file handler

### OpenSTEF Integration

Training uses `train_model_pipeline(pj, train_data, mlflow_tracking_uri=..., artifact_folder=...)`. Forecasting uses `create_forecast_pipeline(pj, to_forecast_data, mlflow_tracking_uri)`. The `PredictionJobDataClass` config is always `forecast_type="demand"`, `resolution_minutes=60`, `quantiles=[0.1, 0.5, 0.9]`. Model type is `'xgb'` (XGBoost) or `'lgb'` (LightGBM), passed as `model` parameter.

Before forecasting, `load` values for the target period are set to `NaN` in `to_forecast_data`; OpenSTEF treats NaN load as the rows to predict.
