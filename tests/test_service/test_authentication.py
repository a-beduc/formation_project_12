import argon2
import pytest

from domain.model import AuthUser
from services import authentication


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
    user = AuthUser(username="Bob", password="hashed_password")
    user.id = 1

    mocker.patch.object(uow.users, "get_by_username", return_value=user)
    mocker.patch.object(argon2.PasswordHasher, "verify", return_value=True)
    assert authentication.login(uow, "Bob", "Password1") == user


def test_login_fail_wrong_username(uow):
    with pytest.raises(authentication.AuthError,
                       match="User not found with not_bob"):
        authentication.login(uow, "not_bob", "pwd")


def test_login_fail_wrong_pwd(uow, mocker):
    user = AuthUser(username="Bob", password="hashed_password")
    mocker.patch.object(uow.users, "get_by_username", return_value=user)
    mocker.patch.object(argon2.PasswordHasher, "verify",
                        side_effect=argon2.exceptions.VerifyMismatchError)
    with pytest.raises(authentication.AuthError, match="Password mismatch"):
        authentication.login(uow, "Bob", "not_pwd")
