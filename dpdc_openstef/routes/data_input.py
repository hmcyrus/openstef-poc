"""Data Input routes"""
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import logging
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from services.weather_service import get_weather_for_date
from services.dropdown_service import _load_holiday_type_options, _load_national_event_options

logger = logging.getLogger(__name__)

# Bangladesh timezone (UTC+6)
TIMEZONE_OFFSET = timezone(timedelta(hours=6))
TIMEZONE_SUFFIX = "+06:00"

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Path to the CSV file
CSV_FILE_PATH = Path("static/master_data_with_forecasted.csv")


@router.get("/data-input", response_class=HTMLResponse)
async def data_input_page(request: Request):
    """Data Input page"""
    return templates.TemplateResponse(
        "data_input.html",
        {
            "request": request,
            "active_page": "data_input",
            "holiday_type_options": _load_holiday_type_options(),
            "national_event_options": _load_national_event_options(),
        },
    )


@router.get("/api/data-input")
async def get_data_input(date: str):
    """API endpoint for fetching predicted and actual data for a specific date"""
    logger.info(f"Fetching data input for date: {date}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(CSV_FILE_PATH)
        # Convert the date_time column from string to pandas datetime objects
        df['date_time'] = pd.to_datetime(df['date_time'])
        
        # Filter data for the selected date (all 24 hours)
        selected_date = pd.to_datetime(date)
        date_data = df[df['date_time'].dt.date == selected_date.date()]
        
        # Prepare hourly data for all 24 hours
        hourly_data = []
        
        # Get common values for is_holiday, holiday_type, national_event_type
        # (they should be the same for all hours in a day)
        if not date_data.empty:
            is_holiday = int(date_data.iloc[0]['is_holiday'])
            holiday_type = int(date_data.iloc[0]['holiday_type'])
            national_event_type = int(date_data.iloc[0]['national_event_type'])
        else:
            is_holiday = 0
            holiday_type = 0
            national_event_type = 0
        
        # Create data for all 24 hours
        for hour in range(24):
            # Find data for this specific hour
            hour_data = date_data[date_data['date_time'].dt.hour == hour]
            
            if not hour_data.empty:
                # Use the actual timestamp from the CSV data
                actual_timestamp = hour_data.iloc[0]['date_time']
                timestamp_str = actual_timestamp.strftime('%Y-%m-%d %H:%M:%S%z')
                # Format timezone offset with colon (e.g., +0600 -> +06:00)
                if len(timestamp_str) > 5 and timestamp_str[-5] in ['+', '-'] and ':' not in timestamp_str[-5:]:
                    timestamp_str = timestamp_str[:-2] + ':' + timestamp_str[-2:]
                load = float(hour_data.iloc[0]['load']) if pd.notna(hour_data.iloc[0]['load']) else 0
                forecasted_load = float(hour_data.iloc[0]['forecasted_load']) if pd.notna(hour_data.iloc[0]['forecasted_load']) else 0
            else:
                # Generate timestamp with +06:00 timezone for missing hours
                timestamp = selected_date + timedelta(hours=hour)
                timestamp_str = timestamp.strftime(f'%Y-%m-%d %H:%M:%S{TIMEZONE_SUFFIX}')
                load = 0
                forecasted_load = 0
            
            hourly_data.append({
                "timestamp": timestamp_str,
                "load": load,
                "forecasted_load": forecasted_load,
                "is_holiday": is_holiday,
                "holiday_type": holiday_type,
                "national_event_type": national_event_type
            })
        
        logger.debug(f"Retrieved {len(hourly_data)} hourly records for date: {date}")
        
        return JSONResponse({"date": date, "data": hourly_data})
    
    except Exception as e:
        logger.error(f"Error fetching data for date {date}: {str(e)}")
        # Return default values if error occurs
        hourly_data = []
        selected_date = pd.to_datetime(date)
        for hour in range(24):
            timestamp = selected_date + timedelta(hours=hour)
            timestamp_str = timestamp.strftime(f'%Y-%m-%d %H:%M:%S{TIMEZONE_SUFFIX}')
            hourly_data.append({
                "timestamp": timestamp_str,
                "load": 0,
                "forecasted_load": 0,
                "is_holiday": 0,
                "holiday_type": 0,
                "national_event_type": 0
            })
        return JSONResponse({"date": date, "data": hourly_data})


@router.post("/api/data-input")
async def update_data_input(
    date: str = Form(...),
    hourly_data: str = Form(...)
):
    """API endpoint for updating predicted and actual data"""
    try:
        data_list = json.loads(hourly_data)
        
        logger.info(f"Updating data for date: {date} with {len(data_list)} records")
        logger.debug(f"Hourly data: {data_list}")
        
        # Extract common values from the first data point
        is_holiday = data_list[0]['is_holiday']
        holiday_type = data_list[0]['holiday_type']
        national_event_type = data_list[0]['national_event_type']
        
        # Create a backup first
        import shutil
        backup_path = CSV_FILE_PATH.with_suffix('.csv.bak')
        if CSV_FILE_PATH.exists():
            shutil.copy2(CSV_FILE_PATH, backup_path)
        
        # Read all lines from the CSV file
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Keep track of which timestamps we're updating
        timestamps_to_update = {hour_data['timestamp']: hour_data for hour_data in data_list}
        timestamps_found = set()
        
        records_updated = 0
        records_created = 0
        
        # Fetch weather data for the date (needed for both updates and creates)
        selected_date = pd.to_datetime(date)
        try:
            weather_data = get_weather_for_date(selected_date)
            logger.info(f"Fetched weather data for {date}: {len(weather_data)} hours")
        except Exception as e:
            logger.error(f"Failed to fetch weather data for {date}: {e}")
            # Use default empty weather data
            weather_data = [{'temp': 0, 'dwpt': 0, 'rhum': 0, 'prcp': 0, 'wdir': 0, 'wspd': 0, 'pres': 0, 'coco': 0} for _ in range(24)]
        
        # Process existing lines and update matching timestamps
        updated_lines = []
        header_line = lines[0] if lines else "date_time,load,is_holiday,holiday_type,national_event_type,temp,dwpt,rhum,prcp,wdir,wspd,pres,coco,forecasted_load\n"
        updated_lines.append(header_line)
        
        # Parse all existing data lines (excluding header and malformed lines)
        existing_data = []
        for i, line in enumerate(lines[1:], 1):  # Skip header
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            parts = line.split(',')
            if len(parts) < 14:  # Skip malformed lines
                logger.warning(f"Skipping malformed line {i}: {line}")
                continue
            
            line_timestamp = parts[0]
            
            # Check if this line's timestamp matches one we need to update
            if line_timestamp in timestamps_to_update:
                hour_data = timestamps_to_update[line_timestamp]
                timestamps_found.add(line_timestamp)
                
                # Get the hour from timestamp to fetch corresponding weather data
                try:
                    timestamp_obj = pd.to_datetime(line_timestamp)
                    hour = timestamp_obj.hour
                    weather_hour = weather_data[hour] if hour < len(weather_data) else weather_data[0]
                    
                    # Update columns: load, is_holiday, holiday_type, national_event_type, weather data, forecasted_load
                    parts[1] = str(hour_data['load'])  # load
                    parts[2] = str(is_holiday)  # is_holiday
                    parts[3] = str(holiday_type)  # holiday_type
                    parts[4] = str(national_event_type)  # national_event_type
                    parts[5] = str(weather_hour['temp'])  # temp
                    parts[6] = str(weather_hour['dwpt'])  # dwpt
                    parts[7] = str(weather_hour['rhum'])  # rhum
                    parts[8] = str(weather_hour['prcp'])  # prcp
                    parts[9] = str(weather_hour['wdir'])  # wdir
                    parts[10] = str(weather_hour['wspd'])  # wspd
                    parts[11] = str(weather_hour['pres'])  # pres
                    parts[12] = str(weather_hour['coco'])  # coco
                    parts[13] = str(hour_data['forecasted_load'])  # forecasted_load
                    records_updated += 1
                except Exception as e:
                    logger.error(f"Error updating weather data for timestamp {line_timestamp}: {e}")
                    # Keep original parts if weather update fails
            
            # Store the line with its timestamp for sorting
            try:
                timestamp_obj = pd.to_datetime(line_timestamp)
                existing_data.append({
                    'timestamp': timestamp_obj,
                    'timestamp_str': line_timestamp,
                    'line': ','.join(parts) + '\n'
                })
            except Exception as e:
                logger.warning(f"Could not parse timestamp '{line_timestamp}': {e}")
                # Still keep the line but with a fallback timestamp
                existing_data.append({
                    'timestamp': pd.Timestamp.max,  # Put unparseable lines at the end
                    'timestamp_str': line_timestamp,
                    'line': ','.join(parts) + '\n'
                })
        
        # Find timestamps that weren't found in the file (need to be created)
        timestamps_to_create = set(timestamps_to_update.keys()) - timestamps_found
        
        if timestamps_to_create:
            # Create new rows for missing timestamps (weather data already fetched above)
            for timestamp_str in timestamps_to_create:
                hour_data = timestamps_to_update[timestamp_str]
                
                try:
                    timestamp_obj = pd.to_datetime(timestamp_str)
                    hour = timestamp_obj.hour
                    
                    # Get weather data for this specific hour
                    weather_hour = weather_data[hour] if hour < len(weather_data) else weather_data[0]
                    
                    # Create row with weather data
                    new_row = (
                        f"{timestamp_str},"
                        f"{hour_data['load']},"
                        f"{is_holiday},"
                        f"{holiday_type},"
                        f"{national_event_type},"
                        f"{weather_hour['temp']},"
                        f"{weather_hour['dwpt']},"
                        f"{weather_hour['rhum']},"
                        f"{weather_hour['prcp']},"
                        f"{weather_hour['wdir']},"
                        f"{weather_hour['wspd']},"
                        f"{weather_hour['pres']},"
                        f"{weather_hour['coco']},"
                        f"{hour_data['forecasted_load']}\n"
                    )
                    
                    existing_data.append({
                        'timestamp': timestamp_obj,
                        'timestamp_str': timestamp_str,
                        'line': new_row
                    })
                    records_created += 1
                except Exception as e:
                    logger.error(f"Could not parse new timestamp '{timestamp_str}': {e}")
        
        # Sort all data by timestamp to maintain chronological order
        existing_data.sort(key=lambda x: x['timestamp'])
        
        # Build the final lines list
        for data in existing_data:
            updated_lines.append(data['line'])
        
        # Write the updated lines back to the file
        with open(CSV_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        # Remove backup file after successful update
        if backup_path.exists():
            backup_path.unlink()
            logger.debug(f"Removed backup file: {backup_path}")
        
        logger.info(f"Data updated successfully for {date}. Updated: {records_updated}, Created: {records_created}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Data updated successfully for {date}. Updated: {records_updated}, Created: {records_created}",
            "records_updated": records_updated + records_created
        })
    
    except Exception as e:
        logger.error(f"Error updating data for date {date}: {str(e)}")
        # Restore from backup if it exists
        backup_path = CSV_FILE_PATH.with_suffix('.csv.bak')
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, CSV_FILE_PATH)
            logger.info("Restored CSV from backup due to error")
        
        return JSONResponse({
            "status": "error",
            "message": f"Failed to update data: {str(e)}",
            "records_updated": 0
        }, status_code=500)