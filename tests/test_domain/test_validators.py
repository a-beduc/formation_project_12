"""Unit tests for ee_crm.domain.validators classes

Tests try to exhaust happy and sad path using pytest parametrization.
"""
from datetime import datetime

import pytest

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
    """Test happy paths."""
    v.CollaboratorValidator.validate_str(string)


@pytest.mark.parametrize(
    "string, err_msg",
    [
        (123456789, "Wrong type must be a string"),
        ("a"*256, "String too long")
    ]
)
def test_validate_str_fail(string, err_msg):
    """Test sad paths.
        * Wrong type,
        * Too long.
    """
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
    """Test happy paths."""
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
    """Test sad paths.
        * Invalid format, missing @,
        * Wrong type,
        * Too long.
    """
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
    """Test happy paths."""
    v.CollaboratorValidator.validate_phone_number(phone_number)


@pytest.mark.parametrize(
    "value_id, err_msg",
    [
        (12, "Phone number must be a string"),
        ("0"*21, "Phone number too long")
    ]
)
def test_validate_phone_number_fail(value_id, err_msg):
    """Test sad paths.
        * Wrong type, missing @,
        * Too long.
    """
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_phone_number(value_id)


def test_validate_id_success():
    """Test happy paths."""
    v.CollaboratorValidator.validate_positive_int(5)


@pytest.mark.parametrize(
    "value_id, err_msg",
    [
        (-5, "Invalid id, must be a positive integer"),
        ("not a number", "Invalid id, must be a positive integer")
    ]
)
def test_validate_id_fail(value_id, err_msg):
    """Test sad paths.
        * Negative integer,
        * Wrong type.
    """
    with pytest.raises(v.CollaboratorValidatorError, match=err_msg):
        v.CollaboratorValidator.validate_positive_int(value_id)


@pytest.mark.parametrize(
    "username",
    [
        "abcd",
        "username",
        "a"*255
    ]
)
def test_validate_username_success(username):
    """Test happy paths."""
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
    """Test sad paths.
        * Too short,
        * Wrong type,
        * Too long.
    """
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
    """Test happy paths."""
    v.AuthUserValidator.validate_password(password)


@pytest.mark.parametrize(
    "password, err_msg",
    [
        ("short1A", "password too weak"),
        ("nouppercase1", "password too weak"),
        ("NOLOWERCASE1", "password too weak"),
        ("NoNumber", "password too weak"),
        (123456789, "Password must be a string"),
        (f"Aa1{'a'*253}", "Password too long")
    ]
)
def test_validate_password_fail(password, err_msg):
    """Test sad paths.
        * Too short,
        * No upper case,
        * No lower case,
        * No number,
        * Wrong type,
        * Too long.
    """
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
    """Test happy paths."""
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
    """Test sad paths.
        * Wrong type,
        * Negative integer,
        * Out of range.
    """
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
    """Test happy paths."""
    v.ContractValidator.validate_price(price)


@pytest.mark.parametrize(
    "price, err_msg",
    [
        ("not a number", "Invalid price type"),
        (-5, "Invalid price value, must be positive")
    ]
)
def test_validate_price_fail(price, err_msg):
    """Test sad paths.
        * Wrong type,
        * Negative value.
    """
    with pytest.raises(v.ContractValidatorError, match=err_msg):
        v.ContractValidator.validate_price(price)


def test_validate_date_success():
    """Test happy paths."""
    v.EventValidator.validate_date(datetime.now())


def test_validate_date_fail():
    """Test sad paths.
        * Wrong type.
    """
    with pytest.raises(v.EventValidatorError, match="Invalid date type"):
        v.EventValidator.validate_date("2025-01-01")


def test_validate_attendee_success():
    """Test happy paths."""
    v.EventValidator.validate_attendee(60)


@pytest.mark.parametrize(
    "number, err_msg",
    [
        ("not a number", "Invalid attendee value, must be a positive integer"),
        (-5, "Invalid attendee value, must be a positive integer")
    ]
)
def test_validate_attendee_fail(number, err_msg):
    """Test sad paths.
        * Wrong type,
        * Negative integer.
    """
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
    """Test happy paths."""
    v.EventValidator.validate_notes(notes)


def test_validate_notes_success_9998_char():
    """Test happy paths, limit of chatacter."""
    notes = "x"*9998
    v.EventValidator.validate_notes(notes)


def test_validate_notes_fail_wrong_type():
    """Test sad paths, wrong type."""
    err_msg = "Invalid notes type, must be a string"
    with pytest.raises(v.EventValidatorError, match=err_msg):
        v.EventValidator.validate_notes(3161)


def test_validate_notes_fail_too_long():
    """Test sad paths, too long."""
    err_msg = "Notes too long, must be less than 9999 characters"
    with pytest.raises(v.EventValidatorError, match=err_msg):
        v.EventValidator.validate_notes("x" * 10000)
