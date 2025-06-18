from datetime import datetime

from ee_crm.exceptions import InputError


def verify_positive_int(value):
    if isinstance(value, int):
        value_int = value
    elif isinstance(value, str) and value.strip().isdigit():
        value_int = int(value.strip())
    else:
        raise InputError("Input must be a valid positive Integer")

    if value_int <= 0:
        raise InputError("Input must be a positive Integer")

    return value_int


def verify_positive_float(value):
    if isinstance(value, (float, int)):
        value_float = value
    elif isinstance(value, str):
        try:
            value_float = float(value.strip())
        except ValueError:
            raise InputError("Input must be a valid Float")
    else:
        raise InputError("Input must be a valid Float")

    if value_float <= 0:
        raise InputError("Input must be a positive Float")

    return value_float


def verify_string(value):
    try:
        return str(value)
    except ValueError:
        raise InputError("Input must be a valid string")


def verify_bool(value):
    if isinstance(value, bool):
        return value
    else:
        raise InputError("Input must be a valid Boolean")


def verify_datetime(value):
    if isinstance(value, datetime):
        return value
    elif isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise InputError("Input must be a valid Datetime")
    else:
        raise InputError("Input must be a valid Datetime")
    