"""Service class for model training and forecasting operations"""
import numpy as np
import pandas as pd
import pickle
import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from openstef.data_classes.prediction_job import PredictionJobDataClass
from openstef.pipeline.train_model import train_model_pipeline
from openstef.pipeline.create_forecast import create_forecast_pipeline
from utils.dateutils import create_utc_datetime
from datetime import datetime, timedelta, timezone
from services.weather_service import get_weather_for_date

# Get logger for this module (configuration is done in main.py)
logger = logging.getLogger(__name__)

PARENT_DIR = "trained_models"
TRAINING_DATA_PATH = "./static/master_data_with_forecasted.csv"

class ModelService:
    """Service class for handling model training and forecasting operations"""
    
    @staticmethod
    def get_trained_models() -> List[str]:
        """Get list of trained model directories"""
        path = Path(PARENT_DIR)
        dirs = [d.name for d in path.iterdir() if d.is_dir()]
        logger.debug(f"Found trained model directories: {dirs}")
        return dirs
    
    @staticmethod
    async def train_model(model: str, custom_name: str, training_data_start_date: str, training_data_end_date: str, hyperparams_dict: Dict[str, Any]) -> str:
        """
        Train a model with given hyperparameters
        
        Args:
            model: Model type (e.g., 'xgb')
            custom_name: Custom name for the model
            training_data_start_date: Start date for training data
            training_data_end_date: End date for training data
            hyperparams_dict: Dictionary of hyperparameters
            
        Returns:
            Status message
        """
        pd.options.plotting.backend = 'plotly'
        pj = dict(
            id=101,
            model='xgb',
            forecast_type="demand",
            horizon_minutes=120,
            resolution_minutes=60,
            name="xgb_poc_1",
            save_train_forecasts=True,
            ignore_existing_models=True,
            model_kwargs={
                "learning_rate": float(hyperparams_dict['learning_rate']),
                "early_stopping_rounds": int(hyperparams_dict['early_stopping_rounds']),
                "n_estimators": int(hyperparams_dict['n_estimators'])
            },
            quantiles=[0.1, 0.5, 0.9]
        )

        pj = PredictionJobDataClass(**pj)

        input_data = pd.read_csv(TRAINING_DATA_PATH, index_col=0, parse_dates=True)

        # dropping columns as we want
        input_data = input_data.drop(columns=["date_time_com", "forecasted_load"])

        pd.options.display.max_columns = None
        logger.debug(f"Input data head:\n{input_data.head()}")

        # Filter data based on provided date range
        start_date = create_utc_datetime(training_data_start_date, 0)
        end_date = create_utc_datetime(training_data_end_date, 23)
        
        # Filter the input data to the specified date range
        train_data = input_data[(input_data.index >= start_date) & (input_data.index <= end_date)]

        logger.info(f"Training data starting hour: {train_data.head(1).index}")
        logger.info(f"Training data ending hour: {train_data.tail(1).index}")
        logger.info(f"Training data filtered from {training_data_start_date} to {training_data_end_date}")

        train_data = train_data[~train_data.index.duplicated(keep='first')]

        # Remove rows with NaT in the index
        train_data = train_data[train_data.index.notna()]

        path_to_create = f"./{PARENT_DIR}/{custom_name}/"

        try:
            os.makedirs(path_to_create, exist_ok=True)
            logger.info(f"Directory structure '{path_to_create}' created successfully.")
        except OSError as e:
            logger.error(f"Error creating directory structure: {e}")
        
        # storing pj for using later
        dictionary_path = f"./{PARENT_DIR}/{custom_name}/pj.pkl"
        with open(dictionary_path, "wb") as file:
            pickle.dump(pj, file, protocol=pickle.HIGHEST_PROTOCOL) 

        mlflow_tracking_uri = f"{PARENT_DIR}/{custom_name}/mlflow_trained_models"

        train_data, validation_data, test_data = train_model_pipeline(
            pj,
            train_data,
            check_old_model_age=False,
            mlflow_tracking_uri=mlflow_tracking_uri,
            artifact_folder=f"{PARENT_DIR}/{custom_name}/mlflow_artifacts",
        )
        return "hello"
    
    @staticmethod
    async def train_model_with_hyperparams(
        model: str, 
        custom_name: str, 
        training_data_start_date: str, 
        training_data_end_date: str, 
        hyperparams_dict: Dict[str, Any]
    ) -> str:
        """
        Train a model with comprehensive hyperparameters
        
        Args:
            model: Model type ('xgb' or 'lgb')
            custom_name: Custom name for the model
            training_data_start_date: Start date for training data
            training_data_end_date: End date for training data
            hyperparams_dict: Dictionary of hyperparameters
            
        Returns:
            Status message
        """
        pd.options.plotting.backend = 'plotly'
        
        # Create PredictionJobDataClass with proper model type and hyperparameters
        pj_dict = dict(
            id=101,
            model=model,  # Use the actual model type from parameter
            forecast_type="demand",
            horizon_minutes=120,
            resolution_minutes=60,
            name=custom_name,  # Use the custom name
            save_train_forecasts=True,
            ignore_existing_models=True,
            model_kwargs=hyperparams_dict,  # Use all hyperparameters from the dictionary
            quantiles=[0.1, 0.5, 0.9]
        )
        
        logger.info(f"Creating PredictionJobDataClass with model={model}, name={custom_name}")
        logger.debug(f"Model kwargs: {hyperparams_dict}")
        
        pj = PredictionJobDataClass(**pj_dict)
        
        # Load training data from default path
        input_data = pd.read_csv(TRAINING_DATA_PATH, index_col=0, parse_dates=True)
        
        # Drop unnecessary columns if they exist
        columns_to_drop = []
        if "date_time_com" in input_data.columns:
            columns_to_drop.append("date_time_com")
        if "forecasted_load" in input_data.columns:
            columns_to_drop.append("forecasted_load")
        
        if columns_to_drop:
            input_data = input_data.drop(columns=columns_to_drop)
        
        pd.options.display.max_columns = None
        logger.debug(f"Input data head:\n{input_data.head()}")
        
        # Filter data based on provided date range
        start_date = create_utc_datetime(training_data_start_date, 0)
        end_date = create_utc_datetime(training_data_end_date, 23)
        
        # Filter the input data to the specified date range
        train_data = input_data[(input_data.index >= start_date) & (input_data.index <= end_date)]
        
        logger.info(f"Training data starting hour: {train_data.head(1).index}")
        logger.info(f"Training data ending hour: {train_data.tail(1).index}")
        logger.info(f"Training data filtered from {training_data_start_date} to {training_data_end_date}")
        
        # Remove duplicate index values
        train_data = train_data[~train_data.index.duplicated(keep='first')]
        
        # Remove rows with NaT in the index
        train_data = train_data[train_data.index.notna()]
        
        # Create directory structure for saving the model
        path_to_create = f"./{PARENT_DIR}/{custom_name}/"
        
        try:
            os.makedirs(path_to_create, exist_ok=True)
            logger.info(f"Directory structure '{path_to_create}' created successfully.")
        except OSError as e:
            logger.error(f"Error creating directory structure: {e}")
            raise
        
        # Persist the training dataset file used for training alongside the model artifacts
        training_data_path = f"./{PARENT_DIR}/{custom_name}/training_data.csv"
        try:
            # Copy the physical CSV file instead of re-saving the DataFrame
            shutil.copy(TRAINING_DATA_PATH, training_data_path)
            logger.info(f"Training data file copied to {training_data_path}")
        except Exception as e:
            logger.error(f"Failed to save training data snapshot: {e}")
            raise
        
        # Store PredictionJob for later use
        dictionary_path = f"./{PARENT_DIR}/{custom_name}/pj.pkl"
        with open(dictionary_path, "wb") as file:
            pickle.dump(pj, file, protocol=pickle.HIGHEST_PROTOCOL)
        
        logger.info(f"PredictionJob saved to {dictionary_path}")
        
        # Save training metadata to JSON file
        metadata = {
            "model": model,
            "custom_name": custom_name,
            "training_data_start_date": training_data_start_date,
            "training_data_end_date": training_data_end_date,
            "hyperparameters": hyperparams_dict,
            "trained_at": datetime.now(timezone.utc).isoformat()
        }
        
        metadata_path = f"./{PARENT_DIR}/{custom_name}/training_metadata.json"
        with open(metadata_path, "w") as file:
            json.dump(metadata, file, indent=4)
        
        logger.info(f"Training metadata saved to {metadata_path}")
        
        # Set up MLflow tracking
        mlflow_tracking_uri = f"{PARENT_DIR}/{custom_name}/mlflow_trained_models"
        
        # Train the model
        logger.info(f"Starting model training for {model} with custom name '{custom_name}'")
        train_data, validation_data, test_data = train_model_pipeline(
            pj,
            train_data,
            check_old_model_age=False,
            mlflow_tracking_uri=mlflow_tracking_uri,
            artifact_folder=f"{PARENT_DIR}/{custom_name}/mlflow_artifacts",
        )
        
        logger.info(f"Model training completed successfully for '{custom_name}'")
        return "Training completed successfully"
    
    @staticmethod
    async def forecast_from_model(custom_name: str, date: str, hour: int) -> Dict[str, Any]:
        """
        Create forecast from a trained model
        
        Args:
            custom_name: Name of the trained model
            date: Date string in format 'YYYY-MM-DD'
            hour: Hour value (0-23)
            
        Returns:
            Dict containing timestamp, forecast value, and custom_name
        """
        input_data = pd.read_csv(TRAINING_DATA_PATH, index_col=0, parse_dates=True)

        
        traing_data_last_index = input_data.index.get_loc(calculate_previous_hr_of_forecast(date, hour))
        # checking if the limit of test data matches our expectation
        test_data = input_data.iloc[traing_data_last_index+1:traing_data_last_index+25]
        logger.info(f"Test data starting hour: {test_data.head(1).index}")
        logger.info(f"Test data ending hour: {test_data.tail(1).index}")

        # Prepare data to make the forecast.
        realised = input_data.loc[test_data.index, 'load'].copy(deep=True)
        to_forecast_data = input_data.copy(deep=True)
        to_forecast_data.loc[test_data.index, 'load'] = np.nan  # clear the load data for the part you want to forecast    
        
        # Remove duplicate index values from train_data
        to_forecast_data = to_forecast_data[~to_forecast_data.index.duplicated(keep='first')]
        # Remove rows with NaT in the index
        to_forecast_data = to_forecast_data[to_forecast_data.index.notna()]
        
        # storing pj for using later
        dictionary_path = f"./{PARENT_DIR}/{custom_name}/pj.pkl"
        with open(dictionary_path, "rb") as file:
            pj = pickle.load(file)

        mlflow_tracking_uri = f"{PARENT_DIR}/{custom_name}/mlflow_trained_models"

        forecast = create_forecast_pipeline(
            pj,
            to_forecast_data,
            mlflow_tracking_uri,
        )

        logger.info(f"Forecast results:\n{forecast}")

        # Create the time index using the utility method
        forecast_timestamp = create_utc_datetime(date, hour)
        
        forecast_value = forecast.loc[forecast_timestamp, 'forecast']
        
        # Return the required JSON structure
        result = {
            "timestamp": create_utc_datetime(date, hour, timezone(timedelta(hours=6))).isoformat(),
            "forecast": float(forecast_value),
            "custom_name": custom_name
        }
        
        logger.info(f"Returning forecast result: {result}")
        return result
    
    @staticmethod
    async def forecast_from_mulitple_models(custom_names: List[str], date: str) -> Dict[str, Any]:
        """
        Create forecasts from multiple trained models for 24 hours (0-23)
        
        Args:
            custom_names: List of trained model names
            date: Date string in format 'YYYY-MM-DD'
            
        Returns:
            Dict with 'all_forecasts' key containing list of model forecasts
        """
        # Load input data and prepare dataframe with NaN for 24 hours
        input_data = pd.read_csv(TRAINING_DATA_PATH, index_col=0, parse_dates=True)
        
        # Calculate the start of the 24-hour forecast period (hour 0 of the given date)
        forecast_start_datetime = create_utc_datetime(date, 0)
        
        # Get the index of the hour before the forecast period starts (robust to missing timestamps)
        traing_data_last_index = get_training_data_last_index(input_data, date)
        
        # Get the test data for the forecast date (only available timestamps)
        test_data = get_test_data_for_date(input_data, date)
        
        # Prepare data to make the forecast - set load values to NaN for the 24 hours
        to_forecast_data = input_data.copy(deep=True)
        to_forecast_data.loc[test_data.index, 'load'] = np.nan
        # Drop all data points after the last test_data timestamp
        if len(test_data) > 0:
            last_test_timestamp = test_data.index[-1]
            to_forecast_data = to_forecast_data[to_forecast_data.index <= last_test_timestamp]
            logger.info(f"Dropped data points after {last_test_timestamp}")
        
        # Remove duplicate index values and NaT
        to_forecast_data = to_forecast_data[~to_forecast_data.index.duplicated(keep='first')]
        to_forecast_data = to_forecast_data[to_forecast_data.index.notna()]
        
        all_forecasts = []
        
        # Extract actual load data for the 24 hours (if available)
        actual_loads = []
        for hour in range(24):
            forecast_timestamp = create_utc_datetime(date, hour)
            # Check if this timestamp exists in the input data
            if forecast_timestamp in input_data.index:
                actual_load = input_data.loc[forecast_timestamp, 'load']
                actual_loads.append({
                    "timestamp": create_utc_datetime(date, hour, timezone(timedelta(hours=6))).isoformat(),
                    "load": float(actual_load) if pd.notna(actual_load) else None
                })
            else:
                actual_loads.append({
                    "timestamp": create_utc_datetime(date, hour, timezone(timedelta(hours=6))).isoformat(),
                    "load": None
                })
        
        # Loop through each model sequentially
        for custom_name in custom_names:
            logger.info(f"Starting forecast for model: {custom_name}")
            
            # Get 24-hour forecasts from this model
            forecast_df = _forecast_24_hours(custom_name, to_forecast_data)
            
            # Format the forecasts for all 24 hours
            model_forecasts = []
            for hour in range(24):
                forecast_timestamp = create_utc_datetime(date, hour)
                
                # Safely access forecast value with error handling
                try:
                    if forecast_timestamp in forecast_df.index and 'forecast' in forecast_df.columns:
                        forecast_value = forecast_df.loc[forecast_timestamp, 'forecast']
                        # Check if the value is valid (not NaN)
                        if pd.notna(forecast_value):
                            forecast_value = float(forecast_value)
                        else:
                            forecast_value = None
                            logger.warning(f"Forecast value is NaN for {custom_name} at {forecast_timestamp}")
                    else:
                        forecast_value = None
                        logger.warning(f"Forecast timestamp {forecast_timestamp} not found in forecast_df for {custom_name}")
                except Exception as e:
                    forecast_value = None
                    logger.error(f"Error accessing forecast value for {custom_name} at {forecast_timestamp}: {e}")
                
                forecast_result = {
                    "timestamp": create_utc_datetime(date, hour, timezone(timedelta(hours=6))).isoformat(),
                    "forecast": forecast_value
                }
                model_forecasts.append(forecast_result)
            
            # Store the model name and its 24-hour forecasts
            model_result = {
                "custom_name": custom_name,
                "model_forecasts": model_forecasts
            }
            all_forecasts.append(model_result)
            logger.info(f"Completed forecast for model: {custom_name}")
        
        logger.info(f"Completed forecasts for all {len(custom_names)} models")
        return {
            "all_forecasts": all_forecasts,
            "actual_loads": actual_loads
        }
    
    @staticmethod
    async def generate_realtime_forecast(
        custom_names: List[str], 
        date: str, 
        holiday: int = 0, 
        holiday_type: int = 0, 
        nation_event: int = 0
    ) -> Dict[str, Any]:
        """
        Generate real-time forecasts from current Dhaka hour to end of day (hour 23)
        
        This method:
        1. Determines current hour in Dhaka timezone
        2. Validates that the selected date is TODAY's date in Dhaka timezone
        3. Extracts historical actual load (hour 0 to current_hour - 1) from CSV
        4. Extracts historical forecasted load (hour 0 to current_hour - 1) from CSV
        5. Creates missing future timestamps with weather data from Meteostat
        6. Generates forecasts for remaining hours (current_hour to 23) using selected models
        
        Args:
            custom_names: List of trained model names
            date: Date string in format 'YYYY-MM-DD' (must be today's date in Dhaka timezone)
            holiday: Holiday indicator (0 or 1)
            holiday_type: Type of holiday (default 0)
            nation_event: National event indicator (default 0)
            
        Returns:
            Dict with structure:
            {
                "current_hour": int,
                "historical_actual": [{"hour": int, "load": float}],
                "historical_forecasted": [{"hour": int, "load": float}],
                "model_forecasts": [
                    {
                        "custom_name": str,
                        "forecasts": [{"hour": int, "forecast": float}]
                    }
                ]
            }
            
        Raises:
            ValueError: If date is not today's date in Dhaka timezone
        """
        # Get current Dhaka date and hour
        dhaka_tz = timezone(timedelta(hours=6))
        current_dhaka_datetime = datetime.now(dhaka_tz)
        current_dhaka_date = current_dhaka_datetime.strftime('%Y-%m-%d')
        current_hour = current_dhaka_datetime.hour
        
        logger.info(f"Current Dhaka time: {current_dhaka_datetime}, Date: {current_dhaka_date}, Hour: {current_hour}")
        
        # Validate that the selected date is today's date in Dhaka timezone
        if date != current_dhaka_date:
            error_msg = (
                f"Real-time forecasting only works for the current date. "
                f"Selected date: {date}, Current Dhaka date: {current_dhaka_date}. "
                f"Please select today's date or use the 'Backtest Models' feature for historical dates."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if it's too late in the day (hour 23)
        if current_hour == 23:
            logger.warning("Current hour is 23. Only one hour remaining to forecast.")
        
        # Validate that models list is not empty
        if not custom_names:
            error_msg = "At least one model must be selected for forecasting."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Load input data with error handling
        try:
            input_data = pd.read_csv(TRAINING_DATA_PATH, index_col=0, parse_dates=True)
        except FileNotFoundError:
            error_msg = f"Training data file not found: {TRAINING_DATA_PATH}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        except Exception as e:
            error_msg = f"Error loading training data: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Extract historical actual load (hour 0 to current_hour - 1)
        historical_actual = []
        for hour in range(0, current_hour):
            timestamp = create_utc_datetime(date, hour)
            if timestamp in input_data.index:
                load = input_data.loc[timestamp, 'load']
                if pd.notna(load):
                    historical_actual.append({
                        "hour": hour,
                        "load": float(load)
                    })
        
        logger.info(f"Extracted {len(historical_actual)} historical actual load values (hours 0-{current_hour-1})")
        
        # Extract historical forecasted load (hour 0 to current_hour - 1)
        historical_forecasted = []
        if 'forecasted_load' in input_data.columns:
            for hour in range(0, current_hour):
                timestamp = create_utc_datetime(date, hour)
                if timestamp in input_data.index:
                    forecasted_load = input_data.loc[timestamp, 'forecasted_load']
                    if pd.notna(forecasted_load):
                        historical_forecasted.append({
                            "hour": hour,
                            "load": float(forecasted_load)
                        })
        
        logger.info(f"Extracted {len(historical_forecasted)} historical forecasted load values (hours 0-{current_hour-1})")
        
        # Prepare data for forecasting (current_hour to 23)
        # Get only the timestamps that exist in the data for the forecast period
        forecast_start = create_utc_datetime(date, current_hour)
        forecast_end = create_utc_datetime(date, 23)
        
        # Filter to get only timestamps within the forecast period that exist in the data
        test_data = input_data[(input_data.index >= forecast_start) & (input_data.index <= forecast_end)]
        
        logger.info(f"Test data contains {len(test_data)} hours from hour {current_hour} to 23 for date {date}")
        
        # Check if we need to create missing timestamps
        expected_hours = list(range(current_hour, 24))
        existing_hours = [ts.hour for ts in test_data.index]
        missing_hours = [h for h in expected_hours if h not in existing_hours]
        
        if missing_hours:
            logger.info(f"Missing {len(missing_hours)} hours in forecast period: {missing_hours}")
            logger.info(f"Creating missing rows and fetching weather data from Meteostat...")
            
            # Fetch weather data for the entire day
            try:
                # Convert date string to datetime for weather service
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                weather_data = get_weather_for_date(date_obj)
                logger.info(f"Successfully fetched weather data for {len(weather_data)} hours")
            except Exception as e:
                logger.error(f"Error fetching weather data: {e}")
                # Use default weather values if fetch fails
                weather_data = [{'temp': 0.0, 'dwpt': 0.0, 'rhum': 0.0, 'prcp': 0.0, 
                               'wdir': 0.0, 'wspd': 0.0, 'pres': 0.0, 'coco': 0} for _ in range(24)]
            
            # Create new rows for missing hours
            new_rows = []
            for hour in missing_hours:
                timestamp = create_utc_datetime(date, hour)
                weather = weather_data[hour] if hour < len(weather_data) else weather_data[0]
                
                # Create a new row with weather data and NaN for load
                new_row = {
                    'load': np.nan,
                    'is_holiday': holiday,
                    'holiday_type': holiday_type,
                    'national_event_type': nation_event,
                    'temp': weather.get('temp', 0.0),
                    'dwpt': weather.get('dwpt', 0.0),
                    'rhum': weather.get('rhum', 0.0),
                    'prcp': weather.get('prcp', 0.0),
                    'wdir': weather.get('wdir', 0.0),
                    'wspd': weather.get('wspd', 0.0),
                    'pres': weather.get('pres', 0.0),
                    'coco': weather.get('coco', 0),
                    'forecasted_load': np.nan
                }
                
                # Create a DataFrame with the timestamp as index
                new_row_df = pd.DataFrame([new_row], index=[timestamp])
                new_rows.append(new_row_df)
            
            # Concatenate new rows with input_data
            if new_rows:
                input_data = pd.concat([input_data] + new_rows)
                input_data = input_data.sort_index()  # Sort by timestamp
                logger.info(f"Added {len(new_rows)} new rows to input_data")
                
                # Re-filter to get updated test_data
                test_data = input_data[(input_data.index >= forecast_start) & (input_data.index <= forecast_end)]
                logger.info(f"Updated test data now contains {len(test_data)} hours")
        
        if len(test_data) > 0:
            logger.info(f"Forecast period starting hour: {test_data.head(1).index[0]}")
            logger.info(f"Forecast period ending hour: {test_data.tail(1).index[0]}")
        
        # Prepare data to make the forecast - set load values to NaN for the forecast period
        to_forecast_data = input_data.copy(deep=True)
        to_forecast_data.loc[test_data.index, 'load'] = np.nan
        
        # Drop all data points after the last test_data timestamp
        if len(test_data) > 0:
            last_test_timestamp = test_data.index[-1]
            to_forecast_data = to_forecast_data[to_forecast_data.index <= last_test_timestamp]
            logger.info(f"Prepared forecast data up to {last_test_timestamp}")
        
        # Remove duplicate index values and NaT
        to_forecast_data = to_forecast_data[~to_forecast_data.index.duplicated(keep='first')]
        to_forecast_data = to_forecast_data[to_forecast_data.index.notna()]
        
        # Generate forecasts for each model
        model_forecasts = []
        for custom_name in custom_names:
            logger.info(f"Generating real-time forecast for model: {custom_name}")
            
            try:
                # Get forecast for remaining hours
                forecast_df = _forecast_24_hours(custom_name, to_forecast_data)
                
                # Extract forecast values for hours that exist in test_data
                forecasts = []
                for timestamp in test_data.index:
                    hour = timestamp.hour
                    
                    try:
                        if timestamp in forecast_df.index and 'forecast' in forecast_df.columns:
                            forecast_value = forecast_df.loc[timestamp, 'forecast']
                            if pd.notna(forecast_value):
                                forecasts.append({
                                    "hour": hour,
                                    "forecast": float(forecast_value)
                                })
                            else:
                                logger.warning(f"Forecast value is NaN for {custom_name} at hour {hour}")
                                forecasts.append({
                                    "hour": hour,
                                    "forecast": None
                                })
                        else:
                            logger.warning(f"Forecast timestamp for hour {hour} not found in forecast_df for {custom_name}")
                            forecasts.append({
                                "hour": hour,
                                "forecast": None
                            })
                    except Exception as e:
                        logger.error(f"Error accessing forecast value for {custom_name} at hour {hour}: {e}")
                        forecasts.append({
                            "hour": hour,
                            "forecast": None
                        })
                
                model_forecasts.append({
                    "custom_name": custom_name,
                    "forecasts": forecasts
                })
                
                logger.info(f"Completed real-time forecast for model: {custom_name}")
                
            except FileNotFoundError:
                error_msg = f"Model files not found for: {custom_name}"
                logger.error(error_msg)
                # Add empty forecast with error indicator for available hours
                model_forecasts.append({
                    "custom_name": custom_name,
                    "forecasts": [{"hour": ts.hour, "forecast": None} for ts in test_data.index],
                    "error": "Model not found"
                })
            except Exception as e:
                error_msg = f"Error generating forecast for {custom_name}: {str(e)}"
                logger.error(error_msg)
                # Add empty forecast with error indicator for available hours
                model_forecasts.append({
                    "custom_name": custom_name,
                    "forecasts": [{"hour": ts.hour, "forecast": None} for ts in test_data.index],
                    "error": str(e)
                })
        
        logger.info(f"Completed real-time forecasts for all {len(custom_names)} models")
        
        return {
            "current_hour": current_hour,
            "historical_actual": historical_actual,
            "historical_forecasted": historical_forecasted,
            "model_forecasts": model_forecasts
        }

def _forecast_24_hours(custom_name: str, to_forecast_data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate 24-hour forecast for a given model using pre-prepared data with NaN values
    
    Args:
        custom_name: Name of the trained model
        to_forecast_data: DataFrame with NaN values for hours to be predicted
        
    Returns:
        DataFrame containing forecast results for 24 hours
    """
    # Load the prediction job configuration
    dictionary_path = f"./{PARENT_DIR}/{custom_name}/pj.pkl"
    with open(dictionary_path, "rb") as file:
        pj = pickle.load(file)
    
    # Set up MLflow tracking URI
    mlflow_tracking_uri = f"{PARENT_DIR}/{custom_name}/mlflow_trained_models"
    
    # Create forecast pipeline
    forecast = create_forecast_pipeline(
        pj,
        to_forecast_data,
        mlflow_tracking_uri,
    )
    
    logger.info(f"Forecast results for {custom_name}:\n{forecast}")
    
    return forecast

def calculate_previous_hr_of_forecast(date: str, hour: int) -> datetime:
    # Create UTC datetime from date and hour parameters
    # Handle hour adjustment logic: if hour > 0, subtract 1; if hour == 0, go to previous date at hour 23
    if hour > 0:
        adjusted_hour = hour - 1
        adjusted_date = date
    else:
        # hour == 0, so we need previous date and hour 23    
        given_date = datetime.strptime(date, '%Y-%m-%d')
        previous_date = given_date - timedelta(days=1)
        adjusted_date = previous_date.strftime('%Y-%m-%d')
        adjusted_hour = 23
    
    return create_utc_datetime(adjusted_date, adjusted_hour)


def get_training_data_last_index(input_data: pd.DataFrame, date: str) -> int:
    """
    Robustly find the index position of the last training data point before forecast period.
    
    Uses searchsorted to handle cases where the exact timestamp doesn't exist in the data.
    
    Args:
        input_data: DataFrame with datetime index containing training data
        date: Forecast date in 'YYYY-MM-DD' format
        
    Returns:
        Integer index position of the last training data point
        
    Raises:
        ValueError: If forecast date is before available training data
    """
    previous_hour = calculate_previous_hr_of_forecast(date, 0)
    
    # Check if the exact timestamp exists
    if previous_hour in input_data.index:
        training_data_last_index = input_data.index.get_loc(previous_hour)
        logger.info(f"Found training data ending at: {previous_hour}")
        return training_data_last_index
    
    # Exact timestamp not found - use searchsorted to find closest position
    insert_pos = input_data.index.searchsorted(previous_hour)
    
    if insert_pos == 0:
        # Requested date is before all available data
        logger.error(f"Forecast date {date} is before available training data")
        raise ValueError(
            f"No training data available before {date}. "
            f"Earliest available data: {input_data.index.min().strftime('%Y-%m-%d')}. "
            f"Please select a later date."
        )
    elif insert_pos >= len(input_data):
        # Requested date is after all available data - use last available index
        logger.warning(f"Previous hour {previous_hour} is after all data. Using last available timestamp.")
        training_data_last_index = len(input_data) - 1
    else:
        # Use the index just before the insertion point
        training_data_last_index = insert_pos - 1
        actual_timestamp = input_data.index[training_data_last_index]
        logger.warning(
            f"Previous hour {previous_hour} not found in data. "
            f"Using closest earlier timestamp: {actual_timestamp}"
        )
    
    return training_data_last_index


def get_test_data_for_date(input_data: pd.DataFrame, date: str) -> pd.DataFrame:
    """
    Extract test data for a specific forecast date, handling missing timestamps gracefully.
    
    Instead of assuming 24 consecutive hours exist, this filters by date range to get
    only the timestamps that actually exist in the data.
    
    Args:
        input_data: DataFrame with datetime index containing all data
        date: Forecast date in 'YYYY-MM-DD' format
        
    Returns:
        DataFrame containing only the available timestamps for the forecast date
    """
    # Define the 24-hour forecast period
    forecast_start = create_utc_datetime(date, 0)
    forecast_end = create_utc_datetime(date, 23)
    
    # Filter to get only timestamps within the forecast period that exist in the data
    test_data = input_data[(input_data.index >= forecast_start) & (input_data.index <= forecast_end)]
    
    # Log information about data availability
    logger.info(f"Test data contains {len(test_data)} hours out of 24 possible for date {date}")
    
    if len(test_data) > 0:
        logger.info(f"Test data starting hour: {test_data.head(1).index[0]}")
        logger.info(f"Test data ending hour: {test_data.tail(1).index[0]}")
        
        # Log any missing hours for debugging
        expected_hours = set(range(24))
        available_hours = set(test_data.index.hour)
        missing_hours = expected_hours - available_hours
        
        if missing_hours:
            logger.warning(f"Missing hours in test data: {sorted(missing_hours)}")
    else:
        logger.warning(f"No data found for forecast date {date}")
    
    return test_data


def get_current_dhaka_hour() -> int:
    """
    Get the current hour in Dhaka timezone (UTC+6)
    
    Returns:
        Integer representing current hour in Dhaka (0-23)
    """
    # Dhaka is UTC+6
    dhaka_tz = timezone(timedelta(hours=6))
    current_dhaka_time = datetime.now(dhaka_tz)
    current_hour = current_dhaka_time.hour
    logger.info(f"Current Dhaka time: {current_dhaka_time}, Hour: {current_hour}")
    return current_hour

