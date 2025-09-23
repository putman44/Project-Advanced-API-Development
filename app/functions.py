import re
from marshmallow import ValidationError
from app.models import db

PHONE_REGEX = re.compile(r"^\d{3}-\d{3}-\d{4}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def strip_strings(data):
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.strip()
    return data


def strip_input(data, **kwargs):
    return strip_strings(data)


def validate_name(value, **kwargs):
    if not value or len(value) < 2:
        raise ValidationError("Name must be at least 2 characters long")
    return value


def validate_email(model, value, **kwargs):
    if not EMAIL_REGEX.match(value):
        raise ValidationError(
            "Invalid email address, must be in format: user@example.com"
        )

    # DB uniqueness check
    existing = db.session.query(model).filter(model.email == value).first()
    if existing:
        raise ValidationError("Email already associated with an account")

    return value


def validate_phone(model, value, **kwargs):
    if not PHONE_REGEX.match(value):
        raise ValidationError("Invalid phone number format (XXX-XXX-XXXX)")

    # DB uniqueness check
    existing = db.session.query(model).filter(model.phone == value).first()
    if existing:
        raise ValidationError("Phone number already associated with an account")

    return value
