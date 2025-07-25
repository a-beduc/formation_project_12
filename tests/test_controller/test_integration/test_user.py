"""Integration test for ee_crm.controllers.app.user

Fixture
    in_memory_uow
        Factory that returns a SqlAlchemyUnitOfWork instance linked to
        the in-memory SQLite database.
    init_db_table_users
        create and populate the table linked to the AuthUser model.
    init_db_table_collaborator
        create and populate the table linked to the Collaborator model.
    bypass_permission_manager
        mock the payload returned by decoding a JWT representing a
        specific MANAGER person.

"""
import pytest

from ee_crm.controllers.app.user import UserManager, UserManagerError
from ee_crm.services.app.users import UserService
from ee_crm.services.dto import AuthUserDTO, CollaboratorDTO


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow):
    """Fixture to replace the Unit of Work class imported by the
    module for one connected to the SQLite in-memory database.

    Autouse is set to True to avoid to forget to add it when testing.
    """
    mocker.patch("ee_crm.controllers.auth.permission.DEFAULT_UOW",
                 return_value=in_memory_uow())
    mocker.patch("ee_crm.controllers.app.user.DEFAULT_UOW",
                 return_value=in_memory_uow())


@pytest.fixture
def bypass_password(mocker):
    """Fixture to bypass the Argon2 password hasher."""
    mocker.patch("ee_crm.domain.model.AuthUser.verify_password",
                 return_value=True)


def test_who_am_i_return_ok(init_db_table_users, init_db_table_collaborator,
                            bypass_permission_manager, in_memory_uow):
    controller = UserManager(UserService(in_memory_uow()))
    auth_dto, coll_dto = controller.who_am_i()

    assert isinstance(auth_dto, AuthUserDTO)
    assert isinstance(coll_dto, CollaboratorDTO)
    assert auth_dto.username == "user_one"
    assert coll_dto.last_name == "col_ln_one"


def test_update_username_ok(init_db_table_users, bypass_permission_manager,
                            in_memory_uow, bypass_password, mocker):
    controller = UserManager(UserService(in_memory_uow()))
    mocker.patch("ee_crm.controllers.app.user.AuthenticationService."
                 "authenticate",
                 return_value={"c_id": 1})
    controller.update_username("user_one", "password", "new_username")

    assert controller.read(pk=1)[0].id == 1
    assert controller.read(pk=1)[0].username == "new_username"


def test_update_username_fail(init_db_table_users, bypass_permission_manager,
                              in_memory_uow, bypass_password, mocker):
    controller = UserManager(UserService(in_memory_uow()))
    mocker.patch("ee_crm.controllers.app.user.AuthenticationService."
                 "authenticate",
                 return_value={"c_id": 2})
    with pytest.raises(UserManagerError,
                       match="You can't modify someone else username."):
        controller.update_username("user_one", "password", "new_username")


def test_update_password_ok(init_db_table_users, bypass_permission_manager,
                            in_memory_uow, bypass_password, mocker):

    def mock_set_password(self, plain_password):
        self._password = plain_password

    service = UserService(in_memory_uow())
    controller = UserManager(service)
    mocker.patch("ee_crm.controllers.app.user.AuthenticationService."
                 "authenticate",
                 return_value={"c_id": 1})
    mocker.patch("ee_crm.domain.model.AuthUser.set_password",
                 new=mock_set_password)

    spy_service = mocker.spy(service, "modify_password")

    controller.update_password("user_one", "oldPASSWORD1", "newPASSWORD1")

    assert spy_service.call_count == 1

    local_uow = in_memory_uow()
    with local_uow:
        assert local_uow.users.get(1)._password == "newPASSWORD1"


def test_update_password_fail(init_db_table_users, bypass_permission_manager,
                              in_memory_uow, bypass_password, mocker):
    controller = UserManager(UserService(in_memory_uow()))
    mocker.patch("ee_crm.controllers.app.user.AuthenticationService."
                 "authenticate",
                 return_value={"c_id": 2})
    with pytest.raises(UserManagerError,
                       match="You can't modify someone else password."):
        controller.update_password("user_one", "oldPASSWORD1", "newPASSWORD1")


def test_verify_plain_password():
    with pytest.raises(UserManagerError, match="passwords do not match"):
        UserManager.verify_plain_password_match("Password1", "Oops-wrong")

