# DPDC OpenSTEF - Load Forecasting Application

A professional FastAPI-based web application for electrical load forecasting with multiple machine learning models.

## Features

- **Train Model**: Configure and train XGBoost or LightGBM models with custom hyperparameters
- **Forecast**: Generate load forecasts with weather data integration and visualization
- **Data Input**: Manage predicted and actual load data by date and hour
- **Dashboard**: Visualize forecast performance with interactive charts

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

The application will be available at: http://localhost:8080

## Pages

### Train Model (/)
- Select model type (XGBoost or LightGBM)
- Configure hyperparameters dynamically based on model selection
- Submit training jobs

### Forecast (/forecast)
- Input forecast parameters (date, hour, holiday info)
- Fetch weather data automatically
- Generate forecasts from multiple models
- View 24-hour forecast charts

### Data Input (/data-input)
- Select date to view/edit data
- Update predicted and actual values for all 24 hours
- Submit batch updates

### Dashboard (/dashboard)
- View daily forecast vs actual comparison
- Compare model performance metrics
- Analyze hourly load patterns
- Key statistics at a glance

## Technology Stack

- **Backend**: FastAPI
- **Frontend**: Bootstrap 5.3, jQuery
- **Charts**: Plotly.js
- **Date Picker**: Flatpickr
- **Select Components**: Select2

## API Endpoints

- `POST /api/train` - Submit model training request
- `POST /api/forecast` - Generate load forecast
- `GET /api/weather` - Fetch weather data
- `GET /api/forecast-chart` - Get 24-hour forecast chart data
- `GET /api/data-input` - Fetch hourly data for a date
- `POST /api/data-input` - Update hourly data
- `GET /api/dashboard-data` - Get dashboard statistics and charts

## Project Structure

```
dpdc_openstef/
├── main.py                    # FastAPI application entry point
├── poc.py                     # Proof of concept script
├── run.bat                    # Windows batch script to run the app
├── run.sh                     # Unix shell script to run the app
├── requirements.txt           # Python dependencies
├── requirements.md            # Requirements documentation
├── README.md                  # This file
├── LOGGING_SETUP.md          # Logging configuration documentation
├── windows_issue.md          # Windows-specific issues documentation
├── routes/                   # API route handlers
│   ├── __init__.py
│   ├── dashboard.py          # Dashboard API endpoints
│   ├── data_input.py         # Data input API endpoints
│   ├── forecast.py           # Forecast API endpoints
│   └── train_model.py        # Model training API endpoints
├── services/                 # Business logic services
│   ├── __init__.py
│   └── model_service.py      # ML model service layer
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template with navigation
│   ├── train_model.html     # Train model page
│   ├── forecast.html        # Forecast page
│   ├── data_input.html      # Data input page
│   └── dashboard.html       # Dashboard page
├── static/                   # Static files and data
│   └── master_data_with_forecasted.csv  # Sample data file
├── utils/                    # Utility modules
│   ├── __init__.py
│   └── logger.py            # Logging utilities
├── logs/                     # Application logs
│   └── app.log              # Main application log file
└── trained_models/           # Stored ML models and artifacts
    ├── after_refact_01/     # Model training run artifacts
    └── test_101/            # Test model artifacts
```

## Notes

- The application currently uses mock data for demonstration purposes
- All API endpoints are designed to be easily integrated with actual ML models and databases
- The UI is fully responsive and works on desktop screens of various sizes

