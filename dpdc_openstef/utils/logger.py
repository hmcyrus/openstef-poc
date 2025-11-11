"""Centralized logging configuration for the application"""
import logging
import sys
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
from io import StringIO


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Configure logging for the entire application.
    Call this once at app startup.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
    
    Example:
        setup_logging(log_level="INFO", log_file="logs/app.log")
    """
    # Create logs directory if logging to file
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Create handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        handlers.append(file_handler)
    
    # Configure root logger with force=True to override any existing configuration
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Get the root logger to ensure all third-party libraries use our handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers and set our handlers
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Configure third-party library loggers to use the same handlers
    third_party_loggers = [
        'openstef',
        'mlflow',
        'sklearn',
        'xgboost',
        'lightgbm',
        'matplotlib',
        'numba'
    ]
    
    for lib_name in third_party_loggers:
        lib_logger = logging.getLogger(lib_name)
        lib_logger.setLevel(logging.INFO)  # Set appropriate level for third-party logs
        lib_logger.handlers.clear()
        for handler in handlers:
            lib_logger.addHandler(handler)
        lib_logger.propagate = True  # Propagate to root logger
    
    # Reduce noise from specific modules
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('numba').setLevel(logging.WARNING)
    
    # Example: Set debug level for specific module
    # logging.getLogger('services.model_service').setLevel(logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")
    logger.info("Third-party library logging configured")


class StreamToLogger:
    """
    Redirect stdout/stderr to logging
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
    
    def flush(self):
        pass


@contextmanager
def capture_outputs(logger_name: str = 'openstef.training'):
    """
    Context manager to capture stdout/stderr and redirect to logging
    
    Usage:
        with capture_outputs('my.logger'):
            # Any print statements or stdout/stderr here will be logged
            print("This will be logged")
    """
    logger = logging.getLogger(logger_name)
    
    # Save original stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    try:
        # Redirect stdout/stderr to logger
        sys.stdout = StreamToLogger(logger, logging.INFO)
        sys.stderr = StreamToLogger(logger, logging.ERROR)
        yield
    finally:
        # Restore original stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr

