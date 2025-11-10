"""Date utility functions for the application"""
from datetime import datetime, timezone


def create_utc_datetime(date_str: str, hour_int: int) -> datetime:
    """
    Create a UTC datetime object from a date string and hour
    
    Args:
        date_str: Date string in format 'YYYY-MM-DD'
        hour_int: Hour value (0-23)
        
    Returns:
        datetime: UTC datetime object with specified date and hour
    """
    dt_naive = datetime.strptime(date_str, '%Y-%m-%d')
    dt_aware_utc = dt_naive.replace(hour=hour_int, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    return dt_aware_utc
