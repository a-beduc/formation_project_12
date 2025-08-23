"""Integration tests for ee_crm.controllers.auth.predicate.

Fixtures
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
"""
import pytest

from ee_crm.controllers.auth.predicate import contract_has_salesman, \
    contract_is_signed, event_has_support, is_client_associated_salesman, \
    is_contract_associated_salesman, is_event_associated_salesman, \
    client_has_salesman, is_event_associated_support
from ee_crm.services.auth.permissions import PermissionService


def auth_payload(c_id, role):
    """Expected payload and returned by decoding the JWT.

    Args
        c_id (int): The ID of the collaborator.
        role (int): The role of the collaborator.
            3 -> MANAGEMENT
            4 -> SALES
            5 -> SUPPORT

    Returns
        dict: The expected payload.
    """
    return {"sub": f"user_{c_id}",
            "c_id": c_id,
            "role": role,
            "name": "test_name"}


@pytest.fixture(autouse=True)
def mock_in_memory_data(mocker, in_memory_uow,
                        init_db_table_users,
                        init_db_table_collaborator,
                        init_db_table_client,
                        init_db_table_contract,
                        init_db_table_event):
    """Fixture to replace the Unit of Work class imported by the
    permission for one connected to the SQLite in-memory database.
    It also initializes the in-memory database with fake data.

    Autouse is set to True to avoid to forget to add it when testing.
    """
    mocker.patch('ee_crm.controllers.auth.permission.DEFAULT_UOW',
                 new=in_memory_uow)


@pytest.fixture
def perm_service(in_memory_uow):
    """Fixture to create a PermissionService connected to the SQLite
    in-memory database."""
    return PermissionService(in_memory_uow())


def test_user_is_client_associated_salesman(perm_service):
    payload = auth_payload(2, 4)
    ctx_1 = {"auth": payload, "pk": 2, "perm_service": perm_service}
    assert is_client_associated_salesman(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 1, "perm_service": perm_service}
    assert is_client_associated_salesman(ctx_2) is False


def test_contract_has_salesman(perm_service):
    ctx_1 = {"pk": 1, "perm_service": perm_service}
    assert contract_has_salesman(ctx_1) is True

    ctx_2 = {"pk": 4, "perm_service": perm_service}
    assert contract_has_salesman(ctx_2) is False


def test_is_contract_associated_salesman(perm_service):
    payload = auth_payload(2, 4)
    ctx_1 = {"auth": payload, "pk": 2, "perm_service": perm_service}
    assert is_contract_associated_salesman(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 1, "perm_service": perm_service}
    assert is_contract_associated_salesman(ctx_2) is False


def test_contract_is_signed(perm_service):
    ctx_1 = {"pk": 1, "perm_service": perm_service}
    assert contract_is_signed(ctx_1) is True

    ctx_2 = {"pk": 3, "perm_service": perm_service}
    assert contract_is_signed(ctx_2) is False


def test_event_has_support(perm_service):
    ctx_1 = {"pk": 1, "perm_service": perm_service}
    assert event_has_support(ctx_1) is True

    ctx_2 = {"pk": 3, "perm_service": perm_service}
    assert event_has_support(ctx_2) is False


def test_is_event_associated_support(perm_service):
    payload = auth_payload(3, 5)
    ctx_1 = {"auth": payload, "pk": 1, "perm_service": perm_service}
    assert is_event_associated_support(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 3, "perm_service": perm_service}
    assert is_event_associated_support(ctx_2) is False


def test_is_event_associated_salesman(perm_service):
    payload = auth_payload(2, 5)
    ctx_1 = {"auth": payload, "pk": 2, "perm_service": perm_service}
    assert is_event_associated_salesman(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 1, "perm_service": perm_service}
    assert is_event_associated_salesman(ctx_2) is False


def test_can_invert_is_event_associated_salesman(perm_service):
    """Test if the function 'is_event_associated_salesman' is correctly
    wrapped by the class P. It verifies that the bitwise operator '~'
    works."""
    payload = auth_payload(2, 5)
    ctx_1 = {"auth": payload, "pk": 2, "perm_service": perm_service}
    assert (~is_event_associated_salesman)(ctx_1) is False

    ctx_2 = {"auth": payload, "pk": 1, "perm_service": perm_service}
    assert (~is_event_associated_salesman)(ctx_2) is True


def test_client_has_salesman(perm_service):
    ctx_1 = {"pk": 2, "perm_service": perm_service}
    assert client_has_salesman(ctx_1) is True

    ctx_2 = {"pk": 4, "perm_service": perm_service}
    assert client_has_salesman(ctx_2) is False
