from datetime import datetime

from ee_crm.exceptions import InputError


def verify_positive_int(value):
    if isinstance(value, int):
        value_int = value
    elif isinstance(value, str) and value.strip().isdigit():
        value_int = int(value.strip())
    else:
        err = InputError("Input must be a valid positive Integer")
        err.tips = "The given value must be an integer (ex:5 or 13)."
        raise err

    if value_int <= 0:
        err = InputError("Input must be a positive Integer")
        err.tips = "The given value must be positive (ex:5 or 13)."
        raise err

    return value_int


def verify_positive_float(value):
    if isinstance(value, (float, int)):
        value_float = value
    elif isinstance(value, str):
        try:
            value_float = float(value.strip())
        except ValueError:
            err = InputError("Input must be a valid Float")
            err.tips = ("The given value must be a valid price "
                        "(ex:12.5 or 15.97).")
            raise err
    else:
        err = InputError("Input must be a valid Float")
        err.tips = "The given value must be a valid price (ex:12.5 or 15.97)."
        raise err

    if value_float <= 0:
        err = InputError("Input must be a positive Float")
        err.tips = "The given value must be a valid price (ex:12.5 or 15.97)."
        raise err

    return value_float


def verify_string(value):
    try:
        return str(value)
    except ValueError:
        err = InputError("Input must be a valid string")
        err.tips = 'The given value must be a text (ex:"Hello World").'
        raise err


def verify_bool(value):
    if isinstance(value, bool):
        return value
    else:
        err = InputError("Input must be a valid Boolean")
        err.tips = "The given value must be a boolean (ex:True or False)."
        raise err


def verify_datetime(value):
    info = ('It must at least contains the year, month and day '
            'following this pattern : '
            '"YYYY-MM-DD". '
            'It can also accept hours, minutes and seconds with '
            'the following pattern : '
            '"YYYY-MM-DD HH:MM:SS".')
    if isinstance(value, datetime):
        return value
    elif isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            err = InputError("Input must be a valid Datetime")
            err.tips = f"The given value must be a valid date. {info}"
            raise InputError("Input must be a valid Datetime")
    else:
        err = InputError("Input must be a valid Datetime")
        err.tips = f"The given value must be a valid date. {info}"
        raise InputError("Input must be a valid Datetime")
    