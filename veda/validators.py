import re
from datetime import datetime

from .exceptions import ValidationError

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\- ]{5,18}[0-9]$")


def is_given(value):
    return value is not None and str(value).strip() != ""


def require_text(value, field):
    if value is None:
        raise ValidationError(f"{field} cannot be empty.")
    text = " ".join(str(value).split())
    if not text:
        raise ValidationError(f"{field} cannot be empty.")
    return text


def parse_number(value, field):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number.")
    if number != number or number in (float("inf"), float("-inf")):
        raise ValidationError(f"{field} must be a valid number.")
    return int(number) if number.is_integer() else round(number, 2)


def require_positive_number(value, field):
    number = parse_number(value, field)
    if number <= 0:
        raise ValidationError(f"{field} must be greater than zero.")
    return number


def require_non_negative_number(value, field):
    number = parse_number(value, field)
    if number < 0:
        raise ValidationError(f"{field} cannot be negative.")
    return number


def require_positive_int(value, field):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a whole number.")
    if number <= 0:
        raise ValidationError(f"{field} must be greater than zero.")
    return number


def require_choice(value, choices, field):
    text = require_text(value, field)
    for choice in choices:
        if choice.lower() == text.lower():
            return choice
    raise ValidationError(f"{field} must be one of: {', '.join(choices)}.")


def validate_email(value):
    text = require_text(value, "Email").lower()
    if not EMAIL_PATTERN.match(text):
        raise ValidationError("Email address is not valid.")
    return text


def validate_phone(value):
    text = require_text(value, "Phone")
    if not PHONE_PATTERN.match(text):
        raise ValidationError("Phone number is not valid.")
    return text


def validate_date(value):
    text = require_text(value, "Date")
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Date must be in YYYY-MM-DD format.")
    return text
