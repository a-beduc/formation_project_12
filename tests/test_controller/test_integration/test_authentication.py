import pytest

from ee_crm.controllers.auth.authentication import login, logout
from ee_crm.services.app.collaborators import CollaboratorService


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow):
    mocker.patch("ee_crm.controllers.auth.authentication.DEFAULT_UOW",
                 return_value=in_memory_uow())


@pytest.fixture
def patch_storage(tmp_path, mocker):
    storage = tmp_path / "tokens.json"
    mocker.patch('ee_crm.services.auth.jwt_handler.get_token_store_path',
                 return_value=str(storage))
    return storage


def test_login_user_and_logout(
        patch_storage,
        in_memory_uow, init_db_table_users, init_db_table_collaborator,
        init_db_table_client,
        init_db_table_contract, init_db_table_event, bypass_permission_sales):
    username = "auth_username"
    password = "Authpassword1"
    data = {
        "last_name": "Jacob",
        "first_name": "Ladders",
    }
    service = CollaboratorService(in_memory_uow())
    service.create(username, password, role="SALES", **data)

    assert service.retrieve(5)[0].last_name == "Jacob"

    login(username, password)

    assert patch_storage.exists()

    logout()

    assert not patch_storage.exists()
