from datetime import date, datetime


def to_isoz_date_string(value: date) -> str:
    return date.strftime(value, "%Y-%m-%d")


def to_isoz_datetime_string(value: datetime) -> str:
    return datetime.strftime(value, "%Y-%m-%dT%H:%M:%SZ")


def from_isoz_date_string(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def from_isoz_datetime_string(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
