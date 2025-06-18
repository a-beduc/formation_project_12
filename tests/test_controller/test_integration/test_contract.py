import pytest
from datetime import datetime

from ee_crm.controllers.app.contract import ContractManager, \
    ContractManagerError
from ee_crm.controllers.permission import AuthorizationDenied
from ee_crm.domain.model import ContractDomainError
from ee_crm.services.app.contracts import ContractService, ContractServiceError
from ee_crm.services.dto import ContractDTO


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow):
    mocker.patch("ee_crm.controllers.permission.SqlAlchemyUnitOfWork",
                 return_value=in_memory_uow())
    mocker.patch("ee_crm.controllers.app.contract.SqlAlchemyUnitOfWork",
                 return_value=in_memory_uow())


def test_read_all_contract(init_db_table_contract,
                           bypass_permission_sales, in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    list_contract = controller.read()

    assert len(list_contract) == 6
    assert isinstance(list_contract[0], ContractDTO)


def test_read_contract_from_pk(init_db_table_contract,
                               bypass_permission_sales,
                               in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    contract = controller.read(1)[0]

    assert contract.total_amount == 100.0
    assert contract.due_amount == 90.0
    assert contract.signed is True
    assert contract.client_id == 1


def test_filter_contracts_signed(init_db_table_contract,
                                 bypass_permission_sales, in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    filters = {"signed": "YES"}
    signed_contracts = controller.read(filters=filters)

    assert len(signed_contracts) == 4
    assert isinstance(signed_contracts[0], ContractDTO)
    assert signed_contracts[0].client_id == 1


def test_sort_contracts_reverse_signed(init_db_table_contract,
                                       bypass_permission_sales,
                                       in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    sort = (("signed", True),)
    list_contracts = controller.read(sort=sort)

    assert len(list_contracts) == 6
    assert list_contracts[0].id == 1
    assert list_contracts[1].id == 2
    assert list_contracts[2].id == 5
    assert list_contracts[3].id == 6
    assert list_contracts[4].id == 3
    assert list_contracts[5].id == 4


def test_create_contract_minimal(init_db_table_collaborator,
                                 init_db_table_client,
                                 init_db_table_contract,
                                 bypass_permission_manager,
                                 in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    data = {"client_id": 3}
    controller.create(**data)

    contract = controller.read(7)[0]

    assert contract.total_amount == 0
    assert contract.due_amount == 0
    assert contract.signed is False
    assert contract.client_id == 3
    assert isinstance(contract.created_at, datetime)


def test_try_create_contract_wrong_role(init_db_table_collaborator,
                                        init_db_table_client,
                                        init_db_table_contract,
                                        bypass_permission_sales,
                                        in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    data = {"client_id": 3}

    with pytest.raises(AuthorizationDenied,
                       match="Permission error in is_management"):
        controller.create(**data)


def test_try_create_contract_client_no_salesman(init_db_table_collaborator,
                                                init_db_table_client,
                                                init_db_table_contract,
                                                bypass_permission_manager,
                                                in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    data = {"client_id": 4}

    with pytest.raises(ContractServiceError,
                       match="Client must have a designated salesman"):
        controller.create(**data)


def test_try_create_contract_client_associated_salesman_is_not_sales(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, bypass_permission_manager, in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))
    data = {"client_id": 1}

    with pytest.raises(ContractServiceError,
                       match="Associated collaborator is not in SALES, "
                             "must reassign client"):
        controller.create(**data)


def test_try_update_contract_directly(init_db_table_contract, in_memory_uow):
    controller = ContractManager(ContractService(in_memory_uow()))

    with pytest.raises(ContractManagerError,
                       match="Can't update contract directly, "
                             "use appropriate methods."):
        controller.update(client_id=1)


def test_try_delete_contract(init_db_table_collaborator, init_db_table_client,
                             init_db_table_contract, in_memory_uow,
                             bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    list_contract = controller.read()
    assert len(list_contract) == 6

    controller.delete(pk=3)

    list_contract = controller.read()
    assert len(list_contract) == 5


def test_try_delete_contract_not_my_client(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))
    with pytest.raises(
            AuthorizationDenied,
            match=r"Permission error in "
                  r"\(\(is_management and not contract_has_salesman\) "
                  r"or "
                  r"\(is_sales and is_contract_associated_salesman\)\)"):
        controller.delete(pk=1)


def test_manager_try_delete_contract_of_salesman(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_manager):
    controller = ContractManager(ContractService(in_memory_uow()))
    with pytest.raises(
            AuthorizationDenied,
            match=r"Permission error in "
                  r"\(\(is_management and not contract_has_salesman\) "
                  r"or "
                  r"\(is_sales and is_contract_associated_salesman\)\)"):
        controller.delete(pk=3)


def test_manager_delete_contract_client_without_salesman(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_manager):
    controller = ContractManager(ContractService(in_memory_uow()))
    list_contract = controller.read()
    assert len(list_contract) == 6

    controller.delete(pk=4)

    list_contract = controller.read()
    assert len(list_contract) == 5


def test_salesman_sign_contract(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract_unsigned = controller.read(3)[0]
    assert contract_unsigned.signed is False

    controller.sign(3)

    contract_signed = controller.read(3)[0]
    assert contract_signed.signed is True


def test_salesman_try_sign_contract_of_not_his_client(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract_unsigned = controller.read(4)[0]
    assert contract_unsigned.signed is False

    with pytest.raises(
            AuthorizationDenied,
            match="Permission error in"):
        controller.sign(4)


def test_salesman_sign_contract_already_signed(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract_signed = controller.read(2)[0]
    assert contract_signed.signed is True

    controller.sign(2)

    # nothing happens
    contract_signed = controller.read(2)[0]
    assert contract_signed.signed is True


def test_salesman_change_total(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(3)[0]
    assert contract.total_amount == 100.0

    controller.change_total(pk=3, total=300)

    contract = controller.read(3)[0]
    assert contract.total_amount == 300.0


def test_salesman_try_change_total_contract_signed(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(2)[0]
    assert contract.signed is True
    assert contract.total_amount == 100.0

    with pytest.raises(
        AuthorizationDenied,
        match=r"Permission error in "
              r"\(\(is_sales and is_contract_associated_salesman\) and "
              r"not contract_is_signed\)"):
        controller.change_total(pk=2, total=300)


def test_salesman_try_change_total_wrong_type(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(3)[0]
    assert contract.total_amount == 100.0

    with pytest.raises(
            ContractManagerError,
            match="Input must be a valid Float"):
        controller.change_total(pk=3, total="wrong data type")

    contract = controller.read(3)[0]
    assert contract.total_amount == 100.0


def test_salesman_pay(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(2)[0]
    assert contract.due_amount == 80.0

    controller.pay(2, 80.0)

    contract = controller.read(2)[0]
    assert contract.due_amount == 0


def test_salesman_pay_too_much(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(2)[0]
    assert contract.due_amount == 80.0

    with pytest.raises(ContractDomainError,
                       match="Payment : 100.0 exceed due. Still due : 80.0"):
        controller.pay(2, 100.0)

    contract = controller.read(2)[0]
    assert contract.due_amount == 80.0


def test_salesman_pay_wrong_type(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(2)[0]
    assert contract.due_amount == 80.0
    with pytest.raises(ContractManagerError,
                       match="Input must be a valid Float"):
        controller.pay(2, "wrong type")

    contract = controller.read(2)[0]
    assert contract.due_amount == 80.0


def test_salesman_pay_contract_not_signed(
        init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, in_memory_uow, bypass_permission_sales):
    controller = ContractManager(ContractService(in_memory_uow()))

    contract = controller.read(3)[0]
    assert contract.due_amount == 100.0
    assert contract.signed is False

    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error in "
                             r"\(\(is_sales and "
                             r"is_contract_associated_salesman\) and "
                             r"contract_is_signed\)"):
        controller.pay(3, 100.0)
