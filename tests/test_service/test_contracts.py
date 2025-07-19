import pytest

from ee_crm.domain.model import (Collaborator, Client, Contract, Role,
                                 ContractDomainError)
from ee_crm.domain.validators import ContractValidatorError
from ee_crm.exceptions import ContractServiceError
from ee_crm.services.app.contracts import ContractService


@pytest.fixture
def init_uow(fake_uow, fake_repo):
    coll_a = Collaborator(first_name="fn_a", last_name="ln_a",
                          _role_id=Role.SALES, _user_id=1)
    coll_b = Collaborator(first_name="fn_b", last_name="ln_b",
                          _role_id=Role.SALES, _user_id=2)
    coll_c = Collaborator(first_name="fn_c", last_name="ln_c",
                          _role_id=Role.MANAGEMENT, _user_id=3)
    fake_uow.collaborators = fake_repo(init=(coll_a, coll_b, coll_c))

    cli_a = Client(last_name="cl_ln_a", first_name="cl_fn_a", _salesman_id=1)
    cli_a.salesman = coll_a

    cli_b = Client(last_name="cl_ln_b", first_name="cl_fn_b", _salesman_id=1)
    cli_b.salesman = coll_a

    cli_c = Client(last_name="cl_ln_c", first_name="cl_fn_c", _salesman_id=2)
    cli_c.salesman = coll_b

    cli_d = Client(last_name="cl_ln_d", first_name="cl_fn_d", _salesman_id=2)
    cli_d.salesman = coll_b

    cli_e = Client(last_name="cl_ln_e", first_name="cl_fn_e", _salesman_id=2)
    cli_e.salesman = coll_b

    fake_uow.clients = fake_repo(
        init=(cli_a, cli_b, cli_c, cli_d, cli_e))

    con_a = Contract(_total_amount=100.00, _client_id=1)
    con_b = Contract(_total_amount=200.00, _client_id=1)
    con_c = Contract(_total_amount=300.00, _client_id=2)
    con_d = Contract(_total_amount=400.00, _client_id=2, _signed=True)
    con_e = Contract(_total_amount=500.00, _client_id=4, _signed=True,
                     _paid_amount=200.00)

    fake_uow.contracts = fake_repo(
        init=(con_a, con_b, con_c, con_d, con_e)
    )
    return fake_uow


def test_create_contract_success(init_uow):
    data = {
        "client_id": 1,
        "total_amount": 600
    }
    service = ContractService(init_uow)
    service.create(**data)

    contract = init_uow.contracts.get(6)

    assert contract.calculate_due_amount() == 600.00


def test_create_contract_failure_bad_price(init_uow):
    data = {
        "client_id": 1,
        "total_amount": -600
    }
    service = ContractService(init_uow)

    with pytest.raises(ContractValidatorError,
                       match="Invalid price value, must be positive"):
        service.create(**data)

def test_create_contract_failure_bad_client(init_uow):
    data = {
        "client_id": 13,
        "total_amount": 600
    }
    service = ContractService(init_uow)

    with pytest.raises(ContractServiceError,
                       match="Contract must be linked to a client"):
        service.create(**data)


def test_sign_contract(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(1)
    assert contract[0].signed is False

    service.sign_contract(1)

    # does nothing
    with pytest.raises(ContractServiceError,
                       match="This contract is already signed"):
        service.sign_contract(1)

    contract = service.retrieve(1)
    assert contract[0].signed is True


def test_change_total_amount_success(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(1)
    assert contract[0].total_amount == 100.00

    service.modify_total_amount(1, 200)
    contract = service.retrieve(1)
    assert contract[0].total_amount == 200.00


def test_change_total_amount_after_signed_fail(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(4)
    assert contract[0].total_amount == 400.00

    with pytest.raises(ContractDomainError, match="Total amount cannot be changed "
                                            "for signed contract"):
        service.modify_total_amount(4, 200)


def test_pay_amount_success(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(4)
    assert contract[0].total_amount == 400.00
    assert contract[0].due_amount == 400.00

    service.pay_amount(4, 400.00)
    contract = service.retrieve(4)
    assert contract[0].total_amount == 400.00
    assert contract[0].due_amount == 0.00


def test_pay_amount_not_signed_fail(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(1)
    assert contract[0].total_amount == 100.00
    assert contract[0].due_amount == 100.00

    with pytest.raises(ContractDomainError, match="Payment can't be registered "
                                            "before signature"):
        service.pay_amount(1, 100.00)


def test_paid_amount_negative_fail(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(4)
    assert contract[0].total_amount == 400.00
    assert contract[0].due_amount == 400.00

    with pytest.raises(ContractDomainError, match="Payment amount must be positive"):
        service.pay_amount(4, -100.00)


def test_paid_amount_exceed_total_fail(init_uow):
    service = ContractService(init_uow)
    contract = service.retrieve(4)
    assert contract[0].total_amount == 400.00
    assert contract[0].due_amount == 400.00

    with pytest.raises(ContractDomainError, match="Payment : 500.0 exceed due. "
                                            "Still due : 400.0"):
        service.pay_amount(4, 500.00)
