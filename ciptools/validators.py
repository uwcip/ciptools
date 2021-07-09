import logging
import re
from typing import Union

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def validate_int(value: Union[str, int]) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValidationError("invalid integer")


def validate_float(value: Union[str, float]) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValidationError("invalid float")


def validate_percentage(value: str) -> int:
    try:
        value = int(re.findall(r"^(\d{1,3})%$", str(value).strip().lower()).pop())
        if value < 0 or value > 100:
            raise ValidationError("alarm threshold must be between 0% and 100%")

        return value
    except (ValueError, TypeError, IndexError):
        raise ValidationError("invalid percentage")


def validate_time_range(value: str) -> int:
    try:
        value = str(value).strip().lower()
        if re.match(r"^([0-9]+[smhd]?)+$", value) is not None:
            time_range = 0
            parts = list(reversed(re.split(r"([smhd])", value)))
            while len(parts):
                # get the number
                part = parts.pop()
                if not part:
                    continue
                else:
                    part = int(part)

                # next piece is the unit
                if len(parts):
                    unit = parts.pop() or ""
                else:
                    unit = ""

                # convert the unit into seconds
                if unit == "m":
                    time_range += part * 60
                elif unit == "h":
                    time_range += part * 3600
                elif unit == "d":
                    time_range += part * 86400
                else:
                    time_range += part

            return time_range
        else:
            raise ValidationError("invalid value for a time range")
    except (TypeError, ValueError):
        raise ValidationError("invalid value for a time range")


def validate_byte_size(value: str) -> int:
    try:
        value = str(value).strip().lower()
        if re.match(r"^([0-9]+[gmkb]?)$", value) is not None:
            byte_size = 0
            parts = list(reversed(re.split(r"([0-9]+)", value)))
            while len(parts):
                # get the number
                part = parts.pop()
                if not part:
                    continue
                else:
                    part = int(part)

                # next piece is the unit
                if len(parts):
                    unit = parts.pop() or ""
                else:
                    unit = ""

                # convert the unit into seconds
                if unit == "g":
                    byte_size += part * 1024 * 1024 * 1024
                elif unit == "m":
                    byte_size += part * 1024 * 1024
                elif unit == "k":
                    byte_size += part * 1024
                else:
                    byte_size += part

            return byte_size
        else:
            raise ValidationError("invalid value for a byte size")
    except Exception:
        raise ValidationError("invalid value for a byte size")
