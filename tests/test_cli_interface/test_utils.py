"""Unit tests for ee_crm.cli_interface.utils"""
from ee_crm.cli_interface.utils import map_accepted_key, clean_sort, \
    normalize_sort, normalize_fields, clean_input_fields, \
    normalize_remove_columns


def test_map_accepted_key():
    accepted_key = {
        "id": {"id"},
        "last_name": {"ln", "last name", "last_name"},
        "first_name": {"fn", "first name", "first_name"},
    }
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name"
    }
    assert map_accepted_key(accepted_key) == mapped_keys


def test_clean_input_fields():
    fields = [("TEST", "tEst"), ("vaLue", 51)]
    cleaned_fields = clean_input_fields(fields)
    assert cleaned_fields == {"test": "tEst", "value": 51}


def test_clean_input_fields_empty():
    fields = []
    cleaned_fields = clean_input_fields(fields)
    assert cleaned_fields is None


def test_clean_sort():
    sort_in = ("data:expected", "unknown:asc", "FN:asc", "lASt_name",
               "role:dESc")
    sort_out = (("data:expected", False), ("unknown", False), ("fn", False),
                ("last_name", False), ("role", True))
    assert clean_sort(sort_in) == sort_out


def test_clean_sort_empty():
    sort_in = ()
    assert clean_sort(sort_in) is None


def test_normalize_sort():
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name",
        "rl": "role",
        "role": "role"
    }
    sort_in = (("data:expected", False), ("unknown", False), ("fn", False),
               ("last_name", False), ("role", True))
    sort_out = (("first_name", False), ("last_name", False), ("role", True))
    assert normalize_sort(sort_in, mapped_keys) == sort_out


def test_normalize_sort_empty():
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name",
        "rl": "role",
        "role": "role"
    }
    sort_in = ()
    assert normalize_sort(sort_in, mapped_keys) is None


def test_normalize_fields():
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name"
    }
    fields_in = {"ln": "Bobby", "first name": "1568"}
    fields_out = {"last_name": "Bobby", "first_name": "1568"}
    assert normalize_fields(fields_in, mapped_keys) == fields_out


def test_normalize_fields_empty():
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name"
    }
    fields_in = {}
    assert normalize_fields(fields_in, mapped_keys) is None


def test_normalize_remove_columns():
    columns_to_normalize = ["last_name", "fn", "unknown"]
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name"
    }
    columns_to_remove = normalize_remove_columns(
        columns_to_normalize, mapped_keys)

    assert columns_to_remove == ["last_name", "first_name"]


def test_normalize_remove_columns_empty():
    columns_to_normalize = []
    mapped_keys = {
        "id": "id",
        "ln": "last_name",
        "last name": "last_name",
        "last_name": "last_name",
        "fn": "first_name",
        "first name": "first_name",
        "first_name": "first_name"
    }
    columns_to_remove = normalize_remove_columns(
        columns_to_normalize, mapped_keys)

    assert columns_to_remove is None
