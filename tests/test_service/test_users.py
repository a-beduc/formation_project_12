import pytest

from ee_crm.services.auth.authentication import AuthenticationError
from ee_crm.services.app.users import UserServiceError, UserService
from ee_crm.domain.model import AuthUser, AuthUserError
from ee_crm.domain.validators import AuthUserValidatorError
from ee_crm.services.dto import AuthUserDTO


def test_retrieve_user_success(uow, fake_repo):
    user = AuthUser(_username="user_b",
                    _password="Password1")
    uow.users = fake_repo(init=(user,))
    service = UserService(uow)
    auth_user_dto = service.retrieve(1)

    assert isinstance(auth_user_dto[0], AuthUserDTO)
    assert auth_user_dto[0].id == 1
    assert auth_user_dto[0].username == "user_b"


def test_retrieve_user_fail(uow):
    service = UserService(uow)
    with pytest.raises(UserServiceError, match="AuthUser not found"):
        service.retrieve(1)


def test_change_password_success(mocker, uow, fake_repo):
    user = AuthUser(_username="user_b",
                    _password="Password1")
    uow.users = fake_repo(init=(user,))
    service = UserService(uow)

    mocker.patch.object(uow.users, "filter_one", return_value=user)
    verify = mocker.patch.object(user, 'verify_password')
    pwd_update = mocker.patch.object(user, 'set_password')

    service.modify_password("user_b", "Password1", "new_pwd")

    verify.assert_called_once_with("Password1")
    pwd_update.assert_called_once_with("new_pwd")


def test_change_password_wrong_username(uow):
    service = UserService(uow)
    with pytest.raises(AuthenticationError,
                       match='No user found with username : "not_bob"'):
        service.modify_password("not_bob", "Password1", "new_pwd")


def test_change_password_fail_wrong_password(mocker, uow, fake_repo):
    user = AuthUser(_username="user_b",
                    _password="Password1")
    uow.users = fake_repo(init=(user,))
    service = UserService(uow)
    verifier = mocker.patch.object(user, 'verify_password')
    verifier.side_effect = AuthUserError('Password mismatch')

    with pytest.raises(AuthUserError, match="Password mismatch"):
        service.modify_password("user_b", "wrong_pwd", "new_pwd")


def test_change_password_fail_new_pwd_too_short(mocker, uow, fake_repo):
    user = AuthUser(_username="user_b",
                    _password="Password1")
    uow.users = fake_repo(init=(user,))
    service = UserService(uow)
    mocker.patch.object(user, 'verify_password')

    with pytest.raises(AuthUserValidatorError,
                       match="password too weak, need at least 8 char, "
                             "1 number, 1 upper, 1 lower"):
        service.modify_password("user_b", "Password1", "ne")


def test_change_username_success(mocker, uow, fake_repo):
    user = AuthUser(_username="user_b",
                    _password="Password1")
    uow.users = fake_repo(init=(user,))
    service = UserService(uow)
    mocker.patch.object(user, 'verify_password')

    service.modify_username("user_b", "Password1", "user_c")

    auth_user_dto = service.retrieve(1)

    assert auth_user_dto[0].username == "user_c"


def test_change_username_fail(mocker, uow, fake_repo):
    user_b = AuthUser(_username="user_b",
                      _password="Password1")
    user_c = AuthUser(_username="user_c",
                      _password="Password1")
    uow.users = fake_repo(init=(user_b, user_c))
    service = UserService(uow)

    mocker.patch.object(user_b, 'verify_password')
    with pytest.raises(UserServiceError,
                       match="User with username user_c already exists"):
        service.modify_username("user_b", "Password1", "user_c")
