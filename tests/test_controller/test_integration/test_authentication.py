"""Integration tests for ee_crm.controllers.auth.authentication

Fixture
    in_memory_uow
        Factory that returns a SqlAlchemyUnitOfWork instance linked to
        the in-memory SQLite database.
    init_db_table_users
        create and populate the table linked to the AuthUser model.
    init_db_table_collaborator
        create and populate the table linked to the Collaborator model.
    init_db_table_client
        create and populate the table linked to the Client model.
    init_db_table_contract
        create and populate the table linked to the Contract model.
    init_db_table_event
        create and populate the table linked to the Event model.
    bypass_permission_sales
        mock the payload returned by decoding a JWT representing a
        specific SALES person.
"""
import pytest

from ee_crm.controllers.auth.authentication import login, logout
from ee_crm.services.app.collaborators import CollaboratorService


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow,
             init_db_table_users,
             init_db_table_collaborator,
             init_db_table_client,
             init_db_table_contract,
             init_db_table_event):
    """Fixture to replace the Unit of Work class imported by the
    authentication for one connected to the SQLite in-memory database.

    Autouse is set to True to avoid to forget to add it when testing.
    """
    mocker.patch("ee_crm.controllers.auth.authentication.DEFAULT_UOW",
                 return_value=in_memory_uow())


@pytest.fixture
def patch_storage(tmp_path, mocker):
    storage = tmp_path / "tokens.json"
    mocker.patch('ee_crm.services.auth.jwt_handler.get_token_store_path',
                 return_value=str(storage))
    return storage


def test_login_user_and_logout(patch_storage, in_memory_uow,
                               bypass_permission_sales):
    username = "auth_username"
    password = "Authpassword1"
    data = {
        "last_name": "Jacob",
        "first_name": "Ladders",
    }
    # Create and persist a new user
    service = CollaboratorService(in_memory_uow())
    service.create(username, password, role="SALES", **data)
    assert service.retrieve(5)[0].last_name == "Jacob"

    # Use the new user credential to login
    login(username, password)

    # Verify the temporary JWT has been created
    assert patch_storage.exists()

    # Verify the temporary JWT has been cleared.
    logout()
    assert not patch_storage.exists()
