import math
from typing import Union

from validators import ValidationError, validate_float, validate_int


def convert_human_seconds(value: Union[str, int]) -> str:
    try:
        value = validate_int(value)
    except ValidationError:
        return "unknown"

    # to 45 seconds
    if value < 45:
        return "a few seconds"

    # to 90 seconds
    if value < 90:
        return "a minute"

    # to 45 minutes
    if value < 2700:
        return f"{math.ceil(value / 60)} minutes"

    # to 90 minutes
    if value < 5400:
        return "an hour"

    # to 21 hours
    if value < 75600:
        return f"{math.ceil(value / 3600)} hours"

    # to 35 hour
    if value < 126000:
        return "a day"

    # to 25 day
    if value < 2160000:
        return f"{math.ceil(value / 86400)} days"

    # to 45 day
    if value < 3888000:
        return "a month"

    # to 319 day
    if value < 27561600:
        return f"{math.ceil(value / 2592000)} months"

    # to 547 day
    if value < 47260800:
        return "a year"

    # more than 547 days ago
    return f"{math.ceil(value / 31536000)} years"


def convert_human_bytes(value: Union[str, int, float]) -> str:
    try:
        value = validate_float(value)
    except ValidationError:
        return "unknown"

    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(value) < 1024.0:
            return f"{value:.1f}{unit}"
        value /= 1024.0
    return f"{value:.1f}Y"
