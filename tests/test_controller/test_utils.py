"""Unit tests for ee_crm.controllers.utils functions.

Tests try to exhaust happy and sad path using pytest parametrization.
"""
from datetime import datetime

import pytest

from ee_crm.controllers.utils import verify_positive_int, \
    verify_positive_float, verify_string, verify_bool, verify_datetime
from ee_crm.exceptions import InputError


@pytest.mark.parametrize(
    "value, expected",
    [
        (7, 7),
        ("42", 42),
        (0, 0)
    ]
)
def test_verify_positive_int_success(value, expected):
    assert verify_positive_int(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        -1,
        "-5",
        "abc",
        5.5,
        None
    ]
)
def test_verify_positive_int_failure(value):
    with pytest.raises(InputError):
        verify_positive_int(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        (3.5, 3.5),
        (10, 10),
        ("12.75", 12.75),
        (0, 0)
    ]
)
def test_verify_positive_float_success(value, expected):
    assert verify_positive_float(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        -0.1,
        "-7.2",
        "abc",
        None
    ]
)
def test_verify_positive_float_failure(value):
    with pytest.raises(InputError):
        verify_positive_float(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Hello", "Hello"),
        (1, "1"),
        (True, "True")
    ]
)
def test_verify_string_success(value, expected):
    assert verify_string(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        True, False
    ]
)
def test_verify_bool_success(value):
    assert verify_bool(value) == value


@pytest.mark.parametrize(
    "value",
    [
        1,
        0,
        "True",
        None
    ]
)
def test_verify_bool_failure(value):
    with pytest.raises(InputError):
        verify_bool(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2025-06-24", datetime(2025, 6, 24)),
        ("2025-06-24 10:15:50", datetime(2025, 6, 24, 10, 15, 50)),
        (datetime(2025, 6, 24, 10, 15, 50), datetime(2025, 6, 24, 10, 15, 50))
    ]
)
def test_verify_datetime_success(value, expected):
    assert verify_datetime(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "2025-13-24",
        "2025-06-32",
        "date ?",
        123,
        None
    ]
)
def test_verify_datetime_failure(value):
    with pytest.raises(InputError):
        verify_datetime(value)
