import json
import os
from datetime import datetime

COUNTER_FILE = "api_counter.json"


def _load_counter() -> dict:
    """Load counter data from disk, or return a fresh structure."""
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"date": "", "month": "", "daily_count": 0, "monthly_count": 0}


def _save_counter(data: dict) -> None:
    """Persist counter data to disk."""
    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_and_increment(daily_limit: int, monthly_limit: int) -> tuple[bool, str]:
    """
    Check whether an API call is allowed, and if so, increment the counters.

    Returns:
        (allowed: bool, message: str)
        - allowed is True if the call can proceed.
        - message explains why a call was blocked, or shows current usage.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")

    data = _load_counter()

    # Reset daily count if the date has changed
    if data.get("date") != today:
        data["date"] = today
        data["daily_count"] = 0

    # Reset monthly count if the month has changed
    if data.get("month") != this_month:
        data["month"] = this_month
        data["monthly_count"] = 0

    # Enforce limits
    if data["daily_count"] >= daily_limit:
        return False, (
            f"Daily API limit reached ({daily_limit} calls). "
            "Please try again tomorrow."
        )
    if data["monthly_count"] >= monthly_limit:
        return False, (
            f"Monthly API limit reached ({monthly_limit} calls). "
            "Please try again next month."
        )

    # Increment and save
    data["daily_count"] += 1
    data["monthly_count"] += 1
    _save_counter(data)

    return True, (
        f"API calls today: {data['daily_count']}/{daily_limit} | "
        f"This month: {data['monthly_count']}/{monthly_limit}"
    )


def get_usage() -> dict:
    """Return current usage stats without modifying counters."""
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")
    data = _load_counter()

    return {
        "daily_count": data["daily_count"] if data.get("date") == today else 0,
        "monthly_count": data["monthly_count"] if data.get("month") == this_month else 0,
    }