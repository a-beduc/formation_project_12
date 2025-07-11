import pytest
from click.testing import CliRunner

from ee_crm.cli_interface.authentication import login, logout


def test_login_success(mocker):
    login_mock = mocker.patch(
        'ee_crm.cli_interface.authentication.authentication.login')
    base_view_class_mock = mocker.patch(
        'ee_crm.cli_interface.authentication.BaseView')
    base_view_instance_mock = base_view_class_mock.return_value

    runner = CliRunner()
    result = runner.invoke(login, input='test_user\ntest_password\n')

    assert result.exit_code == 0
    login_mock.assert_called_once_with('test_user', 'test_password')
    base_view_instance_mock.success.assert_called_once_with(
        "Logged in as test_user! Proceed with your requests")


def test_login_fail(mocker):
    mocker.patch(
        'ee_crm.cli_interface.authentication.authentication.login',
        side_effect=Exception('Password mismatch'))

    runner = CliRunner()
    with pytest.raises(Exception, match='Password mismatch'):
        runner.invoke(login, input='test_user\ntest_password\n',
                      catch_exceptions=False)


def test_logout(mocker):
    logout_mock = mocker.patch(
        'ee_crm.cli_interface.authentication.authentication.logout')
    base_view_class_mock = mocker.patch(
        'ee_crm.cli_interface.authentication.BaseView')
    base_view_instance_mock = base_view_class_mock.return_value

    runner = CliRunner()
    result = runner.invoke(logout)

    assert result.exit_code == 0
    logout_mock.assert_called_once()
    base_view_instance_mock.success.assert_called_once_with(
        "Successfully logged out")
