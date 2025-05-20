import pytest

from domain.model import AuthUser
from services import services
from tests.test_service.mock_uow import FakeUnitOfWork


def test_login_success():
    uow = FakeUnitOfWork()
    uow.users.add(AuthUser(username="bob", password="pwd"))
    logged_user = services.login(uow, "bob", "pwd")
    assert logged_user.username == "bob"


def test_login_fail_wrong_username():
    uow = FakeUnitOfWork()
    uow.users.add(AuthUser(username="bob", password="pwd"))
    with pytest.raises(services.AuthError,
                       match="User not found with not_bob"):
        services.login(uow, "not_bob", "pwd")


def test_login_fail_wrong_pwd():
    uow = FakeUnitOfWork()
    uow.users.add(AuthUser(username="bob", password="pwd"))
    with pytest.raises(services.AuthError, match="Invalid password"):
        services.login(uow, "bob", "not_pwd")
