import argon2
import pytest

from domain.model import AuthUser, Collaborator
from services import jwt_handler, authentication


def test_valid_password_success():
    plain_password = "Password1"
    assert authentication.valid_password(plain_password)


def test_valid_password_fail():
    short_password = "Pwd1"
    no_cap_password = "password1"
    no_min_password = "PASSWORD1"
    no_num_password = "Password"

    assert not authentication.valid_password(short_password)
    assert not authentication.valid_password(no_cap_password)
    assert not authentication.valid_password(no_min_password)
    assert not authentication.valid_password(no_num_password)


def test_valid_username_success(uow):
    assert authentication.valid_username(uow, "Bobby")


def test_valid_username_fail(uow):
    uow.users.add(AuthUser(username="Bobby", password="pwd"))
    assert not authentication.valid_username(uow, "Bobby")
    assert not authentication.valid_username(uow, "Bo")


def test_create_user(uow):
    authentication.create_user(uow, "Bobby", "Password1")

    assert uow.users.get_by_username("Bobby") is not None


def test_login_success(uow, mocker):
    user = AuthUser(username="user_b", password="hashed_password")
    user.id = 1
    collaborator = Collaborator(user_id=user.id, last_name="Ross", first_name="Bobby")
    collaborator.id = 1
    expected_payload = {
        "sub": "user_b",
        "c_id": 1,
        "role": 0,
        "name": "Bobby Ross",
    }
    mocker.patch.object(uow.users, "get_by_username", return_value=user)
    mocker.patch.object(argon2.PasswordHasher, "verify", return_value=True)
    mocker.patch.object(uow.collaborators, "get_by_user_id",
                        return_value=collaborator)

    spy_get_by_username = mocker.spy(uow.users, "get_by_username")
    spy_verify = mocker.spy(argon2.PasswordHasher, "verify")
    spy_get_by_user_id = mocker.spy(uow.collaborators, "get_by_user_id")

    assert authentication.authenticate(uow, "user_b",
                                       "Password1") == expected_payload

    assert spy_get_by_username.call_count == 1
    assert spy_verify.call_count == 1
    assert spy_get_by_user_id.call_count == 1


def test_login_fail_wrong_username(uow):
    with pytest.raises(authentication.AuthError,
                       match="User not found with not_bob"):
        authentication.authenticate(uow, "not_bob", "pwd")


def test_login_fail_wrong_pwd(uow, mocker):
    user = AuthUser(username="Bob", password="hashed_password")
    mocker.patch.object(uow.users, "get_by_username", return_value=user)
    mock_argon = mocker.patch.object(argon2.PasswordHasher, "verify")
    mock_argon.side_effect = argon2.exceptions.VerifyMismatchError

    with pytest.raises(authentication.AuthError, match="Password mismatch"):
        authentication.authenticate(uow, "Bob", "not_pwd")
