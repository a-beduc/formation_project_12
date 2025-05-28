import pytest

from tests.test_service.conftest import FakeRepository

from domain.model import AuthUser, Collaborator, AuthUserError
from services.auth.authentication import (
    AuthenticationService,
    AuthenticationError)


class TestAuthenticate:
    def test_authenticate_success(self, mocker, uow):
        user = AuthUser(username="user_b",
                        password="Password1")
        uow.users = FakeRepository(init=(user,))
        collaborator = Collaborator(user_id=1,
                                    last_name="Ross",
                                    first_name="Bobby")
        uow.collaborators = FakeRepository(init=(collaborator,))

        service = AuthenticationService(uow)
        expected_payload = {
            "sub": "user_b",
            "c_id": 1,
            "role": 1,
            "name": "Bobby Ross",
        }
        mocker.patch.object(uow.users, "filter_one", return_value=user)
        mocker.patch.object(user, "verify_password")
        mocker.patch.object(uow.collaborators,
                            "filter_one",
                            return_value=collaborator)

        spy_filter_by_username = mocker.spy(uow.users, "filter_one")
        spy_verify = mocker.spy(user, "verify_password")
        spy_filter_by_user_id = mocker.spy(uow.collaborators, "filter_one")

        assert service.authenticate("user_b", "Password1") == expected_payload

        assert spy_filter_by_username.call_count == 1
        assert spy_verify.call_count == 1
        assert spy_filter_by_user_id.call_count == 1

    def test_authenticate_fail_wrong_username(self, uow):
        with pytest.raises(AuthenticationError,
                           match="User not found with not_bob"):
            service = AuthenticationService(uow)
            service.authenticate("not_bob", "pwd")

    def test_authenticate_fail_wrong_password(self, uow, mocker):
        user = AuthUser(username="user_b",
                        password="Password1")
        uow.users = FakeRepository(init=(user,))
        collaborator = Collaborator(user_id=1,
                                    last_name="Ross",
                                    first_name="Bobby")
        uow.collaborators = FakeRepository(init=(collaborator,))

        service = AuthenticationService(uow)

        mocker.patch.object(uow.users, "filter_one", return_value=user)
        mock_vp = mocker.patch.object(user, "verify_password")
        mock_vp.side_effect = AuthUserError

        with pytest.raises(AuthenticationError, match="Password mismatch"):
            service.authenticate("user_b", "not_pwd")


def test_change_password_success(uow, mocker):
    user = AuthUser(username="user_b",
                    password="Password1")
    uow.users = FakeRepository(init=(user,))
    service = AuthenticationService(uow)

    mocker.patch.object(uow.users, "filter_one", return_value=user)
    verify = mocker.patch.object(user, 'verify_password')
    pwd_update = mocker.patch.object(user, 'set_password')

    service.change_password("user_b", "Password1", "new_pwd")

    verify.assert_called_once_with("Password1")
    pwd_update.assert_called_once_with("new_pwd")


def test_change_password_wrong_username(uow):
    service = AuthenticationService(uow)
    with pytest.raises(AuthenticationError,
                       match="User not found with not_bob"):
        service.change_password("not_bob", "Password1", "new_pwd")


def test_change_password_fail_wrong_password(mocker, uow):
    user = AuthUser(username="user_b",
                    password="Password1")
    uow.users = FakeRepository(init=(user,))
    service = AuthenticationService(uow)
    mocker.patch.object(uow.users, "filter_one", return_value=user)
    verify = mocker.patch.object(user, "verify_password")
    verify.side_effect = AuthUserError

    with pytest.raises(AuthenticationError, match="Password mismatch"):
        service.change_password("user_b", "wrong_pwd", "new_pwd")


def test_change_password_fail_new_pwd_too_short(mocker, uow):
    user = AuthUser(username="user_b",
                    password="Password1")
    uow.users = FakeRepository(init=(user,))
    service = AuthenticationService(uow)
    mocker.patch.object(uow.users, "filter_one", return_value=user)
    mocker.patch.object(user, 'verify_password')

    with pytest.raises(AuthUserError, match="password too weak, need 8 char, "
                                            "1 number, 1 upper, 1 lower"):
        service.change_password("user_b", "Password1", "ne")
