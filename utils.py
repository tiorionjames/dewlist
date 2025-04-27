from datetime import datetime


def strip_timezone(dt: datetime) -> datetime:
    if dt is not None and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def sanitize_datetime_fields(data: dict) -> dict:
    """
    Automatically strip timezone from any datetime fields in a dict.
    """
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = strip_timezone(value)
    return data
