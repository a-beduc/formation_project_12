from datetime import datetime

import pytest

from ee_crm.domain.model import Collaborator, Role, Contract, Event, Client
from ee_crm.services.app.events import EventService, EventServiceError


@pytest.fixture
def init_uow(fake_uow, fake_repo):
    coll_a = Collaborator(first_name="fn_a", last_name="ln_a",
                          _role_id=Role.SALES, _user_id=1)
    coll_b = Collaborator(first_name="fn_b", last_name="ln_b",
                          _role_id=Role.SUPPORT, _user_id=2)
    coll_c = Collaborator(first_name="fn_c", last_name="ln_c",
                          _role_id=Role.MANAGEMENT, _user_id=3)
    fake_uow.collaborators = fake_repo(init=(coll_a, coll_b, coll_c))

    cli_a = Client(last_name="cl_ln_a", first_name="cl_fn_a", _salesman_id=1)
    cli_b = Client(last_name="cl_ln_b", first_name="cl_fn_b", _salesman_id=1)
    cli_c = Client(last_name="cl_ln_c", first_name="cl_fn_c", _salesman_id=2)
    fake_uow.clients = fake_repo(init=(cli_a, cli_b, cli_c))

    cli_a.salesman = fake_uow.collaborators.get(1)
    cli_b.salesman = fake_uow.collaborators.get(1)
    cli_c.salesman = fake_uow.collaborators.get(2)

    con_a = Contract(_total_amount=100.00, _client_id=1)
    con_b = Contract(_total_amount=200.00, _client_id=1)
    con_c = Contract(_total_amount=300.00, _client_id=2, _signed=True)
    con_d = Contract(_total_amount=400.00, _client_id=2, _signed=True)
    con_e = Contract(_total_amount=500.00, _client_id=4, _signed=True,
                     _paid_amount=200.00)

    con_a.client = fake_uow.clients.get(1)
    con_b.client = fake_uow.clients.get(1)
    con_c.client = fake_uow.clients.get(2)
    con_d.client = fake_uow.clients.get(2)
    con_e.client = None

    fake_uow.contracts = fake_repo(
        init=(con_a, con_b, con_c, con_d, con_e)
    )

    eve_a = Event(title="event_a", start_time=datetime(2025, 1, 1),
                  end_time=datetime(2025, 1, 2), location="address a",
                  attendee=30, notes="notes a", supporter_id=2, _contract_id=5)
    eve_b = Event(_contract_id=4)
    eve_a.contract = fake_uow.contracts.get(5)
    eve_b.contract = fake_uow.contracts.get(4)
    fake_uow.events = fake_repo(
        init=(eve_a, eve_b)
    )

    fake_uow.contracts._store[5].event = eve_a
    fake_uow.contracts._store[4].event = eve_b
    return fake_uow


def test_create_event_success(init_uow):
    data = {
        "title": "test event !",
        "contract_id": 3,
        "useless_payload": "random data"
    }
    service = EventService(init_uow)
    service.create(**data)
    event_dto = service.retrieve(3)

    assert event_dto[0].title == "test event !"
    assert event_dto[0].start_time is None
    assert event_dto[0].contract_id == 3


def test_create_event_no_contract_fail(init_uow):
    data = {
        "title": "test event !"
    }
    service = EventService(init_uow)

    with pytest.raises(EventServiceError, match="No contract found"):
        service.create(**data)


def test_create_event_bad_contract_fail(init_uow):
    data = {
        "title": "test event !",
        "contract_id": 9
    }
    service = EventService(init_uow)

    with pytest.raises(EventServiceError, match="No contract found"):
        service.create(**data)


def test_create_event_contract_not_signed_fail(init_uow):
    data = {
        "title": "test event !",
        "contract_id": 1
    }
    service = EventService(init_uow)

    with pytest.raises(EventServiceError, match="Can't create event for "
                                                "unsigned contracts"):
        service.create(**data)


def test_create_event_already_exists_fail(init_uow):
    data = {
        "title": "test event !",
        "contract_id": 5
    }
    service = EventService(init_uow)
    with pytest.raises(EventServiceError, match="Event already exists."):
        service.create(**data)


def test_assign_support_success(init_uow):
    service = EventService(init_uow)
    service.assign_support(event_id=2, supporter_id=2)
    event_dto = service.retrieve(2)

    assert event_dto[0].supporter_id == 2


def test_assign_support_bad_collaborator_fail(init_uow):
    service = EventService(init_uow)
    with pytest.raises(EventServiceError, match="Can't find collaborator"):
        service.assign_support(event_id=2, supporter_id=10)


def test_assign_support_collaborator_wrong_role_fail(init_uow):
    service = EventService(init_uow)
    with pytest.raises(EventServiceError,
                       match="Can only assign supports to event"):
        service.assign_support(event_id=2, supporter_id=1)


def test_assign_support_remove_support(init_uow):
    service = EventService(init_uow)

    support_id_before = service.retrieve(1)[0].supporter_id
    assert support_id_before == 2

    service.assign_support(event_id=1)

    support_id_after = service.retrieve(1)[0].supporter_id
    assert support_id_after is None
