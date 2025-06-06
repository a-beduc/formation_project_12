import pytest
from datetime import datetime

from ee_crm.domain import validators as v
from ee_crm.domain.model import Role


@pytest.mark.parametrize(
    "string",
    [
        "abc",
        "User One",
        "a"*255
    ]
)
def test_validate_str_success(string):
    v.CollaboratorValidator.validate_str(string)


@pytest.mark.parametrize(
    "string, err_msg",
    [
        (123456789, "Wrong type must be a string"),
        ("a"*256, "String too long")
    ]
)
def test_validate_str_fail(string, err_msg):
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_str(string)


@pytest.mark.parametrize(
    "email",
    [
        "a@c",
        "User@One.b",
        f'{"a"*100}@{"a"*154}'
    ]
)
def test_validate_email_success(email):
    v.CollaboratorValidator.validate_email(email)


@pytest.mark.parametrize(
    "email, err_msg",
    [
        ('invalid-mail', "Email format invalid"),
        (123456789, "Wrong type must be a string"),
        (f'{"a"*100}@{"a"*155}', "String too long")
    ]
)
def test_validate_email_fail(email, err_msg):
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_email(email)


@pytest.mark.parametrize(
    "phone_number",
    [
        "06 06 06 06 06",
        "+339 65 65 65 65",
        "0"*20
    ]
)
def test_validate_phone_number_success(phone_number):
    v.CollaboratorValidator.validate_phone_number(phone_number)


@pytest.mark.parametrize(
    "value_id, err_msg",
    [
        (12, "Phone number must be a string"),
        ("0"*21, "Phone number too long")
    ]
)
def test_validate_phone_number_fail(value_id, err_msg):
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_phone_number(value_id)


def test_validate_id_success():
    v.CollaboratorValidator.validate_id(5)


@pytest.mark.parametrize(
    "value_id, err_msg",
    [
        (-5, "Invalid id, must be a positive integer"),
        ("not a number", "Invalid id, must be a positive integer")
    ]
)
def test_validate_id_fail(value_id, err_msg):
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_id(value_id)


@pytest.mark.parametrize(
    "username",
    [
        "abcd",
        "username",
        "a"*255
    ]
)
def test_validate_username_success(username):
    v.AuthUserValidator.validate_username(username)


@pytest.mark.parametrize(
    "username, err_msg",
    [
        ("abc", "Username too short"),
        (123456789, "Wrong type must be a string"),
        ("a"*256, "String too long")
    ]
)
def test_validate_username_fail(username, err_msg):
    with pytest.raises(v.AuthUserValidatorError, match=err_msg):
        v.AuthUserValidator.validate_username(username)


@pytest.mark.parametrize(
    "password",
    [
        "Password1",
        "XSOpofkspPF56dadzPM?"
    ]
)
def test_validate_password_success(password):
    v.AuthUserValidator.validate_password(password)


@pytest.mark.parametrize(
    "password, err_msg",
    [
        ("short1A", "password too weak, need at least 8 char, 1 number, "
                    "1 upper, 1 lower"),
        ("nouppercase1", "password too weak, need at least 8 char, 1 number, "
                         "1 upper, 1 lower"),
        ("NOLOWERCASE1", "password too weak, need at least 8 char, 1 number, "
                         "1 upper, 1 lower"),
        ("NoNumber", "password too weak, need at least 8 char, 1 number, "
                     "1 upper, 1 lower"),
        (123456789, "Password must be a string"),
        (f"Aa1{'a'*253}", "Password too long")
    ]
)
def test_validate_password_fail(password, err_msg):
    with pytest.raises(v.AuthUserValidatorError, match=err_msg):
        v.AuthUserValidator.validate_password(password)


@pytest.mark.parametrize(
    'role',
    [
        1,
        2,
        Role.MANAGEMENT,
        Role.SALES,
        Role.SUPPORT,
    ]
)
def test_validate_role_success(role):
    v.CollaboratorValidator.validate_role(role)


@pytest.mark.parametrize(
    "role, err_msg",
    [
        ("not a number", "Invalid role"),
        (-5, "Invalid role"),
        (6, "Invalid role")
    ]
)
def test_validate_role_fail(role, err_msg):
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_role(role)


@pytest.mark.parametrize(
    "price",
    [
        0,
        0.01,
        100,
        1000000
    ]
)
def test_validate_price_success(price):
    v.ContractValidator.validate_price(price)


@pytest.mark.parametrize(
    "price, err_msg",
    [
        ("not a number", "Invalid price type"),
        (-5, "Invalid price value, must be positive")
    ]
)
def test_validate_price_fail(price, err_msg):
    with pytest.raises(v.ContractValidatorError, match=err_msg):
        v.ContractValidator.validate_price(price)


def test_validate_date_success():
    v.EventValidator.validate_date(datetime.now())


def test_validate_date_fail():
    with pytest.raises(v.EventValidatorError, match="Invalid date type"):
        v.EventValidator.validate_date("2025-01-01")


def test_validate_attendee():
    v.EventValidator.validate_attendee(60)


@pytest.mark.parametrize(
    "number, err_msg",
    [
        ("not a number", "Invalid attendee value, must be a positive integer"),
        (-5, "Invalid attendee value, must be a positive integer")
    ]
)
def test_validate_attendee(number, err_msg):
    with pytest.raises(v.EventValidatorError, match=err_msg):
        v.EventValidator.validate_attendee(number)

@pytest.mark.parametrize(
    'notes',
    [
        "",
        "a"*20
    ]
)
def test_validate_notes_success(notes):
    v.EventValidator.validate_notes(notes)


def test_validate_notes_success_9998_char():
    notes = "x"*9998
    v.EventValidator.validate_notes(notes)


def test_validate_notes_fail_wrong_type():
    err_msg = "Invalid notes type, must be a string"
    with pytest.raises(v.EventValidatorError, match=err_msg):
        v.EventValidator.validate_notes(3161)


def test_validate_notes_fail_too_long():
    err_msg = "Notes too long, must be less than 9999 characters"
    with pytest.raises(v.EventValidatorError, match=err_msg):
        v.EventValidator.validate_notes("x" * 10000)
