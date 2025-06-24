import pytest

from ee_crm.controllers.auth.predicate import (
    is_client_associated_salesman,
    contract_has_salesman,
    is_contract_associated_salesman,
    contract_is_signed,
    event_has_support,
    is_event_associated_support,
    is_event_associated_salesman, client_has_salesman,
)
from ee_crm.services.auth.permissions import PermissionService


def auth_payload(c_id, role):
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
    mocker.patch('ee_crm.controllers.auth.permission.DEFAULT_UOW',
                 new=in_memory_uow)


@pytest.fixture
def perm_service(in_memory_uow):
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
