import re
import math
from datetime import datetime

def parse_messy_rate(rate_str: str) -> float:
    """Extracts numeric float value from messy rate strings like '$15.5/hr' or ' 20 USD '."""
    if isinstance(rate_str, (int, float)):
        return float(rate_str)
    cleaned = re.sub(r'[^0-9.]', '', str(rate_str))
    return float(cleaned) if cleaned else 0.0

def calculate_fee(entry_time: datetime, exit_time: datetime, hourly_rate: float) -> float:
    """Calculates fee rounding up to the nearest full hour."""
    duration = exit_time - entry_time
    hours = math.ceil(duration.total_seconds() / 3600)
    hours = max(1, hours)  # Minimum 1 hour charge
    return round(hours * hourly_rate, 2)
