from ee_crm.cli_interface.utils import (
    map_accepted_key, clean_sort, normalize_sort, normalize_fields)


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


def test_clean_sort():
    sort_in = ("data:expected", "unknown:asc", "FN:asc", "lASt_name",
               "role:dESc")
    sort_out = (("data:expected", False), ("unknown", False), ("fn", False),
                ("last_name", False), ("role", True))
    assert clean_sort(sort_in) == sort_out


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

