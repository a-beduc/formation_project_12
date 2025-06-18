import pytest

from datetime import datetime

from ee_crm.domain.model import Collaborator, Role, Contract, Event
from ee_crm.services.app.events import EventService, EventServiceError


@pytest.fixture
def init_uow(uow, fake_repo):
    coll_a = Collaborator(first_name="fn_a", last_name="ln_a",
                          _role_id=Role.SALES, _user_id=1)
    coll_b = Collaborator(first_name="fn_b", last_name="ln_b",
                          _role_id=Role.SUPPORT, _user_id=2)
    coll_c = Collaborator(first_name="fn_c", last_name="ln_c",
                          _role_id=Role.MANAGEMENT, _user_id=3)
    uow.collaborators = fake_repo(init=(coll_a, coll_b, coll_c))

    con_a = Contract(_total_amount=100.00, _client_id=1)
    con_b = Contract(_total_amount=200.00, _client_id=1)
    con_c = Contract(_total_amount=300.00, _client_id=2, _signed=True)
    con_d = Contract(_total_amount=400.00, _client_id=2, _signed=True)
    con_e = Contract(_total_amount=500.00, _client_id=4, _signed=True,
                     _paid_amount=200.00)

    uow.contracts = fake_repo(
        init=(con_a, con_b, con_c, con_d, con_e)
    )

    eve_a = Event(title="event_a", start_time=datetime(2025, 1, 1),
                  end_time=datetime(2025, 1, 2), location="address a",
                  attendee=30, notes="notes a", supporter_id=2, _contract_id=5)
    eve_b = Event(_contract_id=4)
    uow.events = fake_repo(
        init=(eve_a, eve_b)
    )
    return uow


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
