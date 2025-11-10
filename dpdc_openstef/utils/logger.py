"""Centralized logging configuration for the application"""
import logging
import sys
from pathlib import Path
from typing import Optional


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
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Optionally set different levels for specific modules
    # Reduce noise from uvicorn access logs
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    
    # Example: Set debug level for specific module
    # logging.getLogger('services.model_service').setLevel(logging.DEBUG)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")

