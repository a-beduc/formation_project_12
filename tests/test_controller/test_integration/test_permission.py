import pytest

from ee_crm.controllers.permission import (
    is_client_associated_salesman,
    contract_has_salesman,
    is_contract_associated_salesman,
    contract_is_signed,
    event_has_support,
    is_event_associated_support,
    is_event_associated_salesman
)


def auth_payload(c_id, role):
    return {"sub": f"user_{c_id}",
            "c_id": c_id,
            "role": role,
            "name": "test_name"}


@pytest.fixture
def mock_in_memory_data(mocker, in_memory_uow,
                        init_db_table_users,
                        init_db_table_collaborator,
                        init_db_table_client,
                        init_db_table_contract,
                        init_db_table_event):
    mocker.patch('ee_crm.controllers.permission.SqlAlchemyUnitOfWork',
                 return_value=in_memory_uow())


def test_user_is_client_associated_salesman(mock_in_memory_data):
    payload = auth_payload(2, 4)
    ctx_1 = {"auth": payload, "pk": 2}
    assert is_client_associated_salesman(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 1}
    assert is_client_associated_salesman(ctx_2) is False


def test_contract_has_salesman(mock_in_memory_data):
    ctx_1 = {"pk": 1}
    assert contract_has_salesman(ctx_1) is True

    ctx_2 = {"pk": 4}
    assert contract_has_salesman(ctx_2) is False


def test_is_contract_associated_salesman(mock_in_memory_data):
    payload = auth_payload(2, 4)
    ctx_1 = {"auth": payload, "pk": 2}
    assert is_contract_associated_salesman(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 1}
    assert is_contract_associated_salesman(ctx_2) is False


def test_contract_is_signed(mock_in_memory_data):
    ctx_1 = {"pk": 1}
    assert contract_is_signed(ctx_1) is True

    ctx_2 = {"pk": 3}
    assert contract_is_signed(ctx_2) is False


def test_event_has_support(mock_in_memory_data):
    ctx_1 = {"pk": 1}
    assert event_has_support(ctx_1) is True

    ctx_2 = {"pk": 3}
    assert event_has_support(ctx_2) is False


def test_is_event_associated_support(mock_in_memory_data):
    payload = auth_payload(3, 5)
    ctx_1 = {"auth": payload, "pk": 1}
    assert is_event_associated_support(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 3}
    assert is_event_associated_support(ctx_2) is False


def test_is_event_associated_salesman(mock_in_memory_data):
    payload = auth_payload(2, 5)
    ctx_1 = {"auth": payload, "pk": 2}
    assert is_event_associated_salesman(ctx_1) is True

    ctx_2 = {"auth": payload, "pk": 1}
    assert is_event_associated_salesman(ctx_2) is False
