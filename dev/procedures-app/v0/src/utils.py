"""
Utility functions for the Procedures Management App
"""

import time
from datetime import datetime, timedelta
from typing import Optional


def generate_id(existing_ids: list) -> int:
    """
    Generate a unique ID by finding the maximum existing ID and adding 1

    Args:
        existing_ids: List of existing IDs

    Returns:
        New unique ID
    """
    if not existing_ids or len(existing_ids) == 0:
        return 1
    return max(existing_ids) + 1


def format_duration(seconds: Optional[float]) -> str:
    """
    Convert seconds to human-readable duration format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2m 30s", "1h 15m", "45s")
    """
    if seconds is None:
        return "N/A"

    # Handle NaN values
    import math
    if math.isnan(seconds):
        return "N/A"

    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero

    Args:
        numerator: Top number
        denominator: Bottom number
        default: Value to return if denominator is zero

    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def validate_procedure_data(name: str, steps: list) -> tuple[bool, Optional[str]]:
    """
    Validate procedure creation data

    Args:
        name: Procedure name
        steps: List of step descriptions

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Procedure name cannot be empty"

    if len(name) > 200:
        return False, "Procedure name must be 200 characters or less"

    if not steps or len(steps) == 0:
        return False, "Procedure must have at least one step"

    if len(steps) > 100:
        return False, "Procedure cannot have more than 100 steps"

    for i, step in enumerate(steps):
        if not step or not step.strip():
            return False, f"Step {i+1} cannot be empty"
        if len(step) > 500:
            return False, f"Step {i+1} must be 500 characters or less"

    return True, None


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string

    Args:
        dt: Datetime object
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    if dt is None:
        return "N/A"

    if isinstance(dt, str):
        # Try to parse if it's already a string
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt

    return dt.strftime(format_str)


def calculate_duration_seconds(start_time: datetime, end_time: Optional[datetime] = None) -> Optional[float]:
    """
    Calculate duration in seconds between two datetimes

    Args:
        start_time: Start datetime
        end_time: End datetime (defaults to now if None)

    Returns:
        Duration in seconds
    """
    if start_time is None:
        return None

    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)

    if end_time is None:
        end_time = datetime.now()
    elif isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)

    duration = end_time - start_time
    return duration.total_seconds()


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
