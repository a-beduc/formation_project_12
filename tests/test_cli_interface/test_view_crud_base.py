"""Unit tests for ee_crm.cli_interface.views.view_base_crud"""
from dataclasses import dataclass

import pytest

from ee_crm.cli_interface.views.view_base_crud import CrudView


@pytest.fixture(autouse=True)
def mock_class_attributes(monkeypatch):
    """Fixture to mock class attributes. It uses monkeypatch to enforce
    the teardown of the classes attributes modifications after each
    test."""
    monkeypatch.setattr(CrudView, "label", "mock label", raising=False)
    monkeypatch.setattr(CrudView, "columns",
                        ["id", "column1", "column2"], raising=False)
    monkeypatch.setattr(CrudView, "weight_width_allocation",
                        {"id": 5, "column1": 10, "column2": 10},
                        raising=False)
    monkeypatch.setattr(CrudView, "max_width_allocation",
                        {"id": 6, "column1": 10, "column2": 20},
                        raising=False)


def test_prepare_chunks():
    view = CrudView()
    text = "this is a text of a fixed length."
    size = 10
    chunks = view._prepare_chunks(text, size)

    expected = ["this is a ", "text of a ", "fixed leng", "th."]

    assert chunks == expected


def test_prepare_header():
    view = CrudView()
    view.allocated_width = {
        "id": 4,
        "column1": 5,
        "column2": 10
    }
    header = view._prepare_header()

    expected = {
        'id': ['id'],
        'column1': ['colum', 'n1'],
        'column2': ['column2']
    }

    assert header == expected


def test_prepare_object(mocker):
    view = CrudView()
    view.allocated_width = {
        "id": 4,
        "column1": 5,
        "column2": 10
    }
    mock_obj = mocker.Mock()
    mock_obj.id = 5
    mock_obj.column1 = "value"
    mock_obj.column2 = "This is a longer than weight value"

    object_lines = view._prepare_object(mock_obj)

    expected = {
        "id": ["5"],
        "column1": ["value"],
        "column2": ["This is a ", "longer tha", "n weight v", "alue"],
    }

    assert object_lines == expected


def test_make_separator():
    view = CrudView()
    view.allocated_width = {
        "id": 4,
        "column1": 5,
        "column2": 10
    }
    separator = view._make_separator()

    expected = "║ ────┼─────┼────────── ║"

    assert separator == expected


def test_calculate_col_width():
    view = CrudView()
    available_width = 30
    allocated_column_width = view._calculate_col_width("column2",
                                                       available_width)

    # available width * column2 weight / sum of all weight = expected
    # 30 * 10 / (10 + 10 + 5) = 12
    expected = 12

    assert allocated_column_width == expected


def test_spread_extra_space():
    view = CrudView()
    view.allocated_width = {
        "id": 4,
        "column1": 5,
        "column2": 10
    }
    available_width = 10 + sum(view.allocated_width.values())
    view._spread_extra_space(available_width)

    expected = {
        "id": 6,
        "column1": 9,
        "column2": 14
    }

    assert view.allocated_width == expected


def test_calculate_table_and_col_width(mocker):
    mocker.patch("ee_crm.cli_interface.views.view_base_crud.get_terminal_size",
                 return_value=mocker.Mock(columns=25))
    view = CrudView()
    table_width = view._calculate_table_and_col_width()

    expected = 24

    assert table_width == expected


def test_construct_top_line():
    table_width = 24
    view = CrudView()
    top_line = view._construct_top_line(table_width)

    expected = "╔══ mock label Table ══╗"

    assert top_line == expected


def test_transform_row_to_lines():
    view = CrudView()
    view.allocated_width = {
        "id": 4,
        "column1": 5,
        "column2": 10
    }
    cell_chunks = {
        "id": ["5"],
        "column1": ["value"],
        "column2": ["This is a ", "longer tha", "n weight v", "alue"],
    }
    lines = view._transform_row_to_lines(cell_chunks)

    expected = [
        '║ 5   │value│This is a  ║',
        '║     │     │longer tha ║',
        '║     │     │n weight v ║',
        '║     │     │alue       ║'
    ]

    assert lines == expected


def test_create_table(mocker):
    @dataclass
    class MockObject:
        id: int
        column1: str
        column2: str

    # patch terminal size
    mocker.patch("ee_crm.cli_interface.views.view_base_crud.get_terminal_size",
                 return_value=mocker.Mock(columns=25))

    # some random object to put in a list
    obj_1 = MockObject(id=5,
                       column1="value",
                       column2="This is a longer than weight value")
    obj_2 = MockObject(id=6,
                       column1="thing",
                       column2="Not longer")
    obj_3 = MockObject(id=7,
                       column1="longer value",
                       column2="short")

    view = CrudView()
    lines = view._create_table([obj_1, obj_2, obj_3])

    expected = [
        '╔══ mock label Table ══╗',
        '║                      ║',
        '║ id  │column1│column2 ║',
        '║ ────┼───────┼─────── ║',
        '║ 5   │value  │This is ║',
        '║     │       │ a long ║',
        '║     │       │er than ║',
        '║     │       │ weight ║',
        '║     │       │ value  ║',
        '║ ────┼───────┼─────── ║',
        '║ 6   │thing  │Not lon ║',
        '║     │       │ger     ║',
        '║ ────┼───────┼─────── ║',
        '║ 7   │longer │short   ║',
        '║     │value  │        ║',
        '╚══════════════════════╝'
    ]

    assert lines == expected


def test_render_empty(mocker):
    view = CrudView()
    spy_error = mocker.spy(view, 'error')
    view.render(data=None)

    spy_error.assert_called_once_with("No mock label found.")


def test_render_remove_column(mocker):
    view = CrudView()

    spy_create = mocker.spy(view, '_create_table')
    spy_print = mocker.spy(view, '_print')

    @dataclass
    class MockObject:
        id: int
        column1: str
        column2: str

    data = [MockObject(id=1, column1="value", column2="This value is removed")]

    view.render(data, remove_col=["column2"])

    assert view.instance_columns == ['id', 'column1']

    # stock the list of formatted string
    created_lines = spy_create.spy_return

    # verify that the list is given to the _print func
    spy_print.assert_called_once_with(created_lines)

