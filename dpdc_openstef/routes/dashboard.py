"""Dashboard routes"""
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Path to the CSV file
CSV_FILE_PATH = Path("static/master_data_with_forecasted.csv")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})

@router.get("/api/dashboard/data")
async def get_dashboard_data(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Fetch data from CSV for a given date range.
    Constraints:
    - Max range: 30 days
    - Max end_date: Today
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Validations
        if end > today:
            return JSONResponse(
                status_code=400,
                content={"detail": "End date cannot be in the future."}
            )
        
        if (end - start).days > 30:
            return JSONResponse(
                status_code=400,
                content={"detail": "Date range cannot exceed 30 days."}
            )
        
        if end < start:
             return JSONResponse(
                status_code=400,
                content={"detail": "End date cannot be before start date."}
            )

        if not CSV_FILE_PATH.exists():
             return JSONResponse(
                status_code=404,
                content={"detail": "Data file not found."}
            )

        # Read CSV
        df = pd.read_csv(CSV_FILE_PATH)
        df['date_time'] = pd.to_datetime(df['date_time'], utc=True)

        # Convert comparison dates to timezone-aware (UTC)
        start_tz = pd.Timestamp(start, tz='UTC')
        end_tz = pd.Timestamp(end, tz='UTC')
        
        # Adjust end to include the whole day
        end_full = end_tz + timedelta(days=1) - timedelta(seconds=1)

        # Filter
        mask = (df['date_time'] >= start_tz) & (df['date_time'] <= end_full)
        filtered_df = df.loc[mask].copy()
        
        # Sort
        filtered_df.sort_values('date_time', inplace=True)
        
        # Convert NaNs to None/null for JSON
        filtered_df = filtered_df.replace({np.nan: None})

        # Convert timestamp to string for JSON serialization
        filtered_df['date_time'] = filtered_df['date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        records = filtered_df.to_dict(orient='records')
        
        return JSONResponse(content={"data": records})

    except ValueError as ve:
        return JSONResponse(status_code=400, content={"detail": f"Invalid date format: {str(ve)}"})
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@router.get("/api/dashboard/health")
async def check_dashboard_health(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Check data health for a given range.
    Health criteria:
    - Data point exists for each hour (0-23) of each date.
    - load != 0
    - forecasted_load != 0
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end < start:
             return JSONResponse(
                status_code=400,
                content={"detail": "End date cannot be before start date."}
            )

        if not CSV_FILE_PATH.exists():
             return JSONResponse(
                status_code=404,
                content={"detail": "Data file not found."}
            )

        df = pd.read_csv(CSV_FILE_PATH)
        df['date_time'] = pd.to_datetime(df['date_time'], utc=True)
        
        # Convert to timezone-aware timestamps for comparison
        start_tz = pd.Timestamp(start, tz='UTC')
        end_tz = pd.Timestamp(end, tz='UTC')
        
        # Generate all expected hourly timestamps (timezone-aware)
        expected_timestamps = []
        current = start_tz
        end_full_day = end_tz + timedelta(days=1)
        
        while current < end_full_day:
            for hour in range(24):
                ts = current + timedelta(hours=hour)
                if ts < end_full_day:
                    expected_timestamps.append(ts)
            current += timedelta(days=1)

        # Filter DF to relevant range to optimize
        mask = (df['date_time'] >= start_tz) & (df['date_time'] < end_full_day)
        subset = df.loc[mask].copy()
        
        # Set index to timestamp for easy lookup
        subset.set_index('date_time', inplace=True)
        
        missing_points = []
        
        for expected_ts in expected_timestamps:
            # Check existence
            if expected_ts not in subset.index:
                missing_points.append({
                    "timestamp": expected_ts.strftime('%Y-%m-%d %H:%M:%S'),
                    "reason": "Missing record"
                })
                continue
            
            # Get row (handle duplicates if any, take first)
            row = subset.loc[expected_ts]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            
            # Check values
            load = row.get('load', 0)
            forecasted = row.get('forecasted_load', 0)
            
            reasons = []
            if pd.isna(load) or load == 0:
                reasons.append("Zero/Null Load")
            if pd.isna(forecasted) or forecasted == 0:
                reasons.append("Zero/Null Forecast")
                
            if reasons:
                missing_points.append({
                    "timestamp": expected_ts.strftime('%Y-%m-%d %H:%M:%S'),
                    "reason": ", ".join(reasons)
                })

        return JSONResponse(content={
            "missing_count": len(missing_points),
            "missing_points": missing_points
        })

    except Exception as e:
        logger.error(f"Error checking dashboard health: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
