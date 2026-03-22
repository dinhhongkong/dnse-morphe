from __future__ import annotations

from datetime import date, datetime

__all__ = ["parse_date", "parse_datetime"]


def parse_date(value: str | date | None) -> date | None:
    """Parse a date from string, date, or None."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        if "T" in value or " " in value:
            dt = parse_datetime(value)
            return dt.date() if dt else None
        return datetime.strptime(value, "%Y-%m-%d").date()
    return None


def parse_datetime(value: str | datetime | int | float | None) -> datetime | None:
    """Parse a datetime from string, datetime, or timestamp."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    if isinstance(value, str):
        value = value.strip()
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
        raise ValueError(f"Cannot parse datetime from: {value!r}")
    return None
