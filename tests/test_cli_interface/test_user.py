import pytest
from click.testing import CliRunner

from ee_crm.cli_interface.app.user import user


@pytest.fixture
def runner():
    return CliRunner()


def test_user_cli_read(mocker, runner):
    """Too much mocking for being interesting tests."""
    keys_map = mocker.patch(
        "ee_crm.cli_interface.app.user.KEYS_MAP",
        return_value={"dummy": "dummy"}
    )
    manager = mocker.patch(
        "ee_crm.cli_interface.app.user.UserManager",
        autospec=True
    )
    output = mocker.patch(
        "ee_crm.cli_interface.app.user.cli_read",
        return_value=["output"])
    remove_col = mocker.patch(
        "ee_crm.cli_interface.app.user.normalize_remove_columns",
        return_value=["column_to_remove"])
    viewer = mocker.patch("ee_crm.cli_interface.app.user.UserCrudView",
                          autospec=True)

    result = runner.invoke(user, [
        "read",
        "-pk", "3"
    ])

    assert result.exit_code == 0

    output.assert_called_once_with(3, (), (), manager, keys_map)
    remove_col.assert_called_once()
    viewer().render.assert_called_once_with(
        ["output"], remove_col=["column_to_remove"])
