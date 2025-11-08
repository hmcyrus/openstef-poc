# Import all required packages.
from openstef.data_classes.prediction_job import PredictionJobDataClass
from openstef.pipeline.train_model import train_model_pipeline
from IPython.display import IFrame
import pandas as pd
import os

pd.options.plotting.backend = 'plotly'
pj = dict(id=101,
        model='xgb',
        forecast_type="demand",
        horizon_minutes=120,
        resolution_minutes=60,
        name="xgb_poc_1",
        save_train_forecasts=True,
        ignore_existing_models=True,
        model_kwargs = {
          "learning_rate": 0.01,
          "early_stopping_rounds": 10,
          "n_estimators": 50
        },
        quantiles=[0.1, 0.5, 0.9]
       )

pj=PredictionJobDataClass(**pj)

input_data=pd.read_csv("./static/master_data_with_forecasted.csv", index_col=0, parse_dates=True)

# print(input_data.head())

# Inspect all column names of the input data
# print("columns in csv")
# print(input_data.columns)

# dropping columns as we want
input_data = input_data.drop(columns=["date_time_com", "forecasted_load"])
# print("remaining columns after dropping")
# print(input_data.columns)

pd.options.display.max_columns = None
print(input_data.head())


traing_data_last_index = input_data.index.get_loc('2025-06-15 23:00:00+00:00')
train_data=input_data.iloc[:traing_data_last_index+1]

print(f"starting hour of training_data {train_data.head(1).index}")
print(f"ending hour of training_data {train_data.tail(1).index}")

# cleaning up training data by removing duplicate indices and non-datetime indices
# Remove duplicate index values from train_data
train_data = train_data[~train_data.index.duplicated(keep='first')]

# Remove rows with NaT in the index
train_data = train_data[train_data.index.notna()]



mlflow_dir = "./mlflow_trained_models"
# mlflow_tracking_uri = os.path.abspath(mlflow_dir)
# mlflow_tracking_uri = "file:///" + os.path.abspath(mlflow_dir).replace("\\", "/")
mlflow_tracking_uri = "mlflow_trained_models"


# train_data, validation_data, test_data = train_model_pipeline(
#     pj,
#     train_data,
#     check_old_model_age=False,
#     mlflow_tracking_uri=mlflow_tracking_uri,
#     artifact_folder="./mlflow_artifacts",
# )

# checking if the limit of test data matches our expectation
test_data=input_data.iloc[traing_data_last_index+1:traing_data_last_index+25]
# print(test_data.head())

print(f"starting hour of test_data {test_data.head(1).index}")
print(f"ending hour of test_data {test_data.tail(1).index}")


import numpy as np
from openstef.pipeline.create_forecast import create_forecast_pipeline

# Prepare data to make the forecast.
realised=input_data.loc[test_data.index, 'load'].copy(deep=True)
to_forecast_data=input_data.copy(deep=True)
to_forecast_data.loc[test_data.index, 'load']=np.nan #clear the load data for the part you want to forecast

# Remove duplicate index values from train_data
to_forecast_data = to_forecast_data[~to_forecast_data.index.duplicated(keep='first')]

# Remove rows with NaT in the index
to_forecast_data = to_forecast_data[to_forecast_data.index.notna()]

# Location where the model was stored in the last exercise.
mlflow_tracking_uri="mlflow_trained_models"

forecast=create_forecast_pipeline(
    pj,
    to_forecast_data,
    mlflow_tracking_uri,
)

print(forecast.loc[test_data.index])
