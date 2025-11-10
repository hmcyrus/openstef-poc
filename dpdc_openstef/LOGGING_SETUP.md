# Centralized Logging Configuration

## Overview
This document describes the centralized logging setup implemented for the DPDC OpenSTEF application.

## Architecture

### Centralized Configuration
- **Location**: `utils/logger.py`
- **Initialization**: `main.py` (at application startup)
- **Pattern**: Module-level loggers with centralized configuration

### Benefits
✅ **Traceability** - Each log shows which module it came from  
✅ **Flexibility** - Can configure different log levels per module  
✅ **Production-ready** - Logs to both console and file  
✅ **Maintainability** - Easy to add logging to new modules  
✅ **Industry standard** - Follows Python logging best practices  

## File Structure

```
dpdc_openstef/
├── utils/
│   ├── __init__.py
│   └── logger.py          # Centralized logging configuration
├── main.py                # Initializes logging at startup
├── services/
│   └── model_service.py   # Uses module-level logger
└── routes/
    ├── train_model.py     # Uses module-level logger
    ├── forecast.py        # Uses module-level logger
    ├── data_input.py      # Uses module-level logger
    └── dashboard.py       # Uses module-level logger
```

## Usage

### 1. Configuration (Done Once at Startup)

In `main.py`:
```python
from utils.logger import setup_logging

# Setup logging once at startup
setup_logging(log_level="INFO", log_file="logs/app.log")
```

### 2. Using Logger in Any Module

In any Python file:
```python
import logging

logger = logging.getLogger(__name__)

# Then use:
logger.debug("Detailed debugging information")
logger.info("General informational messages")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical error messages")
```

## Log Levels

- **DEBUG**: Detailed information for diagnosing problems (e.g., DataFrame contents, detailed parameters)
- **INFO**: Confirmation that things are working as expected (e.g., requests received, operations completed)
- **WARNING**: Something unexpected happened, but the application is still working
- **ERROR**: A serious problem occurred, some functionality failed
- **CRITICAL**: A very serious error, the application may be unable to continue

## Log Output

### Console Output
All logs are printed to stdout with timestamps and module names:
```
2025-11-09 10:30:45,123 - __main__ - INFO - DPDC OpenSTEF application started successfully
2025-11-09 10:30:46,456 - services.model_service - INFO - Found trained model directories: ['test_101']
2025-11-09 10:30:47,789 - routes.train_model - INFO - Training request received - Model: xgb, Custom Name: test_model
```

### File Output
Logs are also written to `logs/app.log` for persistence and debugging.

## Configuration Options

### Change Log Level
Edit `main.py`:
```python
# For more verbose logging (includes DEBUG messages)
setup_logging(log_level="DEBUG", log_file="logs/app.log")

# For less verbose logging (only WARNING and above)
setup_logging(log_level="WARNING", log_file="logs/app.log")
```

### Module-Specific Log Levels
Edit `utils/logger.py`:
```python
# Set debug level for specific module
logging.getLogger('services.model_service').setLevel(logging.DEBUG)

# Reduce noise from uvicorn
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
```

### Disable File Logging
Edit `main.py`:
```python
# Only log to console
setup_logging(log_level="INFO", log_file=None)
```

## Examples

### Services (model_service.py)
```python
logger.info(f"Found trained model directories: {dirs}")
logger.debug(f"Input data head:\n{input_data.head()}")
logger.error(f"Error creating directory structure: {e}")
```

### Routes (train_model.py)
```python
logger.info(f"Training request received - Model: {model}, Custom Name: {custom_name}")
logger.debug(f"Hyperparameters: {hyperparams_dict}")
logger.info(f"Training initiated successfully for {model} model")
```

## Migration from print()

All `print()` statements have been replaced with appropriate logger calls:

| Old Code | New Code | Reason |
|----------|----------|--------|
| `print(dirs)` | `logger.info(f"Found directories: {dirs}")` | Important info |
| `print(input_data.head())` | `logger.debug(f"Data:\n{input_data.head()}")` | Debug detail |
| `print(f"Error: {e}")` | `logger.error(f"Error: {e}")` | Error message |

## Best Practices

1. **Use appropriate log levels** - Don't log everything as INFO
2. **Include context** - Add relevant information to log messages
3. **Avoid sensitive data** - Don't log passwords, API keys, etc.
4. **Use f-strings** - More readable than string concatenation
5. **Log exceptions properly** - Use `logger.exception()` in except blocks

## Future Enhancements

Consider adding:
- Log rotation (to prevent log files from growing too large)
- Structured logging (JSON format for easier parsing)
- Remote logging (send logs to a centralized logging service)
- Request ID tracking (trace requests across multiple modules)

