import pytest
from click.testing import CliRunner

from ee_crm.cli_interface.app.cli_func import cli_clean, cli_prompt, \
    cli_create, cli_read, cli_update, cli_confirm, cli_delete, cli_mine


def test_cli_clean(mocker):
    clean_fields = mocker.patch(
        "ee_crm.cli_interface.app.cli_func.clean_input_fields",
        return_value={"a": 1, "c": "info"}
    )
    norm_fields = mocker.patch(
        "ee_crm.cli_interface.app.cli_func.normalize_fields",
        return_value={"a": 1}
    )
    clean_sorts = mocker.patch(
        "ee_crm.cli_interface.app.cli_func.clean_sort",
        return_value=(("b", True), ("c", False))
    )
    norm_sorts = mocker.patch(
        "ee_crm.cli_interface.app.cli_func.normalize_sort",
        return_value=(("b", True),)
    )
    filters_in = [("A", 1), ('c', "info")]
    sorts_in = ["B:desc", "C:asc"]
    keys_map = {"a": "A", "b": "B"}
    filters, sorts = cli_clean(filters_in, sorts_in, keys_map)

    assert filters == {"a": 1}
    assert sorts == (("b", True),)
    clean_fields.assert_called_once_with(filters_in)
    norm_fields.assert_called_once_with({"a": 1, "c": "info"}, keys_map)
    clean_sorts.assert_called_once_with(sorts_in)
    norm_sorts.assert_called_once_with((("b", True), ("c", False)), keys_map)


@pytest.mark.parametrize(
    "label, data, user_input, no_prompt_flag, prompt_called, expected_result",
    [
        ("no_data", {},
         ["input_a", "input_b", "input_c"], False, 3,
         {"a": "input_a", "b": "input_b", "c": "input_c"}),

        ("partial_data", {"b": "input_b"},
         ["input_a", "input_c"], False, 2,
         {"a": "input_a", "b": "input_b", "c": "input_c"}),

        ("full_data", {"a": "input_a", "b": "input_b", "c": "input_c"},
         [], False, 0,
         {"a": "input_a", "b": "input_b", "c": "input_c"}),

        ("no_data_no_prompt", {},
         [], True, 0,
         {}),
    ]
)
def test_cli_prompt(mocker, label, data, user_input, no_prompt_flag,
                    prompt_called, expected_result):
    prompt_mock = mocker.patch("ee_crm.cli_interface.app.cli_func.click.prompt",
                               side_effect=user_input)

    prompt_fields = (
        ("a", "string"),
        ("b", "value random"),
        ("c", "20 character max")
    )
    result = cli_prompt(data, no_prompt_flag, prompt_fields)

    assert prompt_mock.call_count == prompt_called
    assert result == expected_result


def test_cli_create(mocker):
    class MockManager:
        pass

        def create(self, **kwargs):
            return {"id": 1, **kwargs}

    mocker.patch("ee_crm.cli_interface.app.cli_func.clean_input_fields",
                 return_value={"foo": "bar"})
    mocker.patch("ee_crm.cli_interface.app.cli_func.normalize_fields",
                 return_value={"foo": "bar"})
    mocker.patch("ee_crm.cli_interface.app.cli_func.cli_prompt",
                 return_value={"foo": "bar"})

    result = cli_create(data_input=[("foo", "bar")],
                        no_prompt=True,
                        ctrl_class=MockManager,
                        prompt_field=[],
                        keys_map={}
                        )

    assert result == {"id": 1, "foo": "bar"}


def test_cli_read(mocker):
    class MockManager:
        pass

        def read(self, pk, filters, sorts):
            return pk, filters, sorts

    mocker.patch("ee_crm.cli_interface.app.cli_func.cli_clean",
                 return_value=({"id": 1}, ("id", True)))

    result = cli_read(pk=1,
                      filters=("id", 1),
                      sorts=("id:desc",),
                      ctrl_class=MockManager,
                      keys_map={})

    assert result == (1, {'id': 1}, ('id', True))


def test_cli_confirm_abort(mocker):
    class MockManagerError(Exception):
        pass

    class MockManager:
        label = "label"
        error_cls = MockManagerError

    mocker.patch("ee_crm.cli_interface.app.cli_func.click.confirm",
                 side_effect=[False])

    with pytest.raises(MockManagerError, match="Aborted by user"):
        cli_confirm(pk=1, ctrl_inst=MockManager(), msg="message")


def test_cli_update(mocker):
    class MockManager:
        label = "label"
        updated = None

        @classmethod
        def update(cls, pk, **kwargs):
            cls.updated = pk, kwargs

    mocker.patch("ee_crm.cli_interface.app.cli_func.click.confirm",
                 side_effect=[False])
    mocker.patch("ee_crm.cli_interface.app.cli_func.cli_confirm")

    mocker.patch("ee_crm.cli_interface.app.cli_func.clean_input_fields",
                 return_value={"foo": "bar"})
    mocker.patch("ee_crm.cli_interface.app.cli_func.normalize_fields",
                 return_value={"foo": "bar"})
    mocker.patch("ee_crm.cli_interface.app.cli_func.cli_prompt",
                 return_value={"foo": "bar"})

    cli_update(pk=1,
               data_input=[("foo", "bar")],
               no_prompt=True,
               ctrl_class=MockManager,
               prompt_field=[],
               keys_map={})

    assert MockManager.updated == (1, {'foo': 'bar'})


def test_cli_delete(mocker):
    class MockManager:
        label = "label"
        data_to_delete = {1: {'foo': 'bar'}, 2: {'foo': 'bar'}}

        @classmethod
        def delete(cls, pk):
            cls.data_to_delete.pop(pk)

    mocker.patch("ee_crm.cli_interface.app.cli_func.cli_confirm")

    cli_delete(pk=1, ctrl_class=MockManager)

    assert MockManager.data_to_delete == {2: {'foo': 'bar'}}


def test_cli_mine(mocker):
    class MockManager:
        @classmethod
        def user_associated_resource(cls, norm_filters, norm_sorts, **kwargs):
            return [norm_filters, norm_sorts, kwargs]

    mocker.patch("ee_crm.cli_interface.app.cli_func.cli_clean",
                 return_value=[{'filter': 'value'}, [('id', True)]])

    result = cli_mine(filters=("foo", "bar"),
                      sorts=("id:desc",),
                      ctrl_class=MockManager,
                      keys_map={})

    assert result == [{'filter': 'value'}, [('id', True)], {}]
