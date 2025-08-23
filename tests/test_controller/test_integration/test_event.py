"""Integration tests for ee_crm.controllers.app.event

Fixtures
    in_memory_uow
        Factory that returns a SqlAlchemyUnitOfWork instance linked to
        the in-memory SQLite database.
    init_db_table_collaborator
        create and populate the table linked to the Collaborator model.
    init_db_table_client
        create and populate the table linked to the Client model.
    init_db_table_contract
        create and populate the table linked to the Contract model.
    init_db_table_event
        create and populate the table linked to the Event model.
    bypass_permission_manager
        mock the payload returned by decoding a JWT representing a
        specific MANAGER person.
    bypass_permission_sales
        mock the payload returned by decoding a JWT representing a
        specific SALES person.
    bypass_permission_support
        mock the payload returned by decoding a JWT representing a
        specific SUPPORT person.
"""
import pytest

from ee_crm.controllers.app.event import EventManager
from ee_crm.controllers.auth.permission import AuthorizationDenied
from ee_crm.exceptions import EventManagerError
from ee_crm.services.app.events import EventService, EventServiceError
from ee_crm.services.dto import EventDTO


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow):
    """Fixture to replace the Unit of Work class imported by the
    module for one connected to the SQLite in-memory database.

    Autouse is set to True to avoid to forget to add it when testing.
    """
    mocker.patch("ee_crm.controllers.auth.permission.DEFAULT_UOW",
                 return_value=in_memory_uow())
    mocker.patch("ee_crm.controllers.app.event.DEFAULT_UOW",
                 return_value=in_memory_uow())


def test_read_all_events(init_db_table_event,
                         in_memory_uow,
                         bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))

    list_event = controller.read()

    assert len(list_event) == 4
    assert isinstance(list_event[0], EventDTO)


def test_filter_events(init_db_table_event,
                       in_memory_uow,
                       bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    filters = {"location": "location_fou"}

    events = controller.read(filters=filters)

    assert len(events) == 1
    assert events[0].id == 4


def test_filter_events_supporter_id(init_db_table_event,
                                    in_memory_uow,
                                    bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    filters = {"supporter_id": "3"}
    events = controller.read(filters=filters)

    assert len(events) == 2
    assert events[0].id == 1
    assert events[1].id == 2


def test_sort_events_supporter_id(init_db_table_event,
                                  in_memory_uow,
                                  bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    sort = (('supporter_id', False),)
    events = controller.read(sort=sort)

    assert len(events) == 4
    assert events[0].id == 3
    assert events[1].id == 4
    assert events[2].id == 1
    assert events[3].id == 2


def test_create_event_minimal(init_db_table_collaborator,
                              init_db_table_client,
                              init_db_table_contract,
                              init_db_table_event,
                              in_memory_uow,
                              bypass_permission_sales):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"contract_id": "6"}

    assert len(controller.read()) == 4

    controller.create(**data)

    assert len(controller.read()) == 5
    assert controller.read()[4].contract_id == 6


def test_create_event_bad_date(init_db_table_collaborator,
                               init_db_table_client,
                               init_db_table_contract,
                               init_db_table_event,
                               in_memory_uow,
                               bypass_permission_sales):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"contract_id": "6",
            "start_time": "bad date"}

    assert len(controller.read()) == 4
    with pytest.raises(EventManagerError,
                       match="Input must be a valid Datetime"):
        controller.create(**data)


def test_create_event_bad_int(init_db_table_collaborator,
                              init_db_table_client,
                              init_db_table_contract,
                              init_db_table_event,
                              in_memory_uow,
                              bypass_permission_sales):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"contract_id": "6",
            "attendee": "bad value"}

    assert len(controller.read()) == 4
    with pytest.raises(EventManagerError,
                       match="Input must be a valid positive Integer"):
        controller.create(**data)


def test_sales_update_event_without_support(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event, bypass_permission_sales):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"title": "new_title"}

    event = controller.read(3)[0]
    assert event.title == "title_thr"
    assert event.supporter_id is None

    controller.update(3, **data)

    event = controller.read(3)[0]
    assert event.title == "new_title"


def test_sales_cant_update_event_with_support(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event, bypass_permission_sales):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"title": "new_title"}

    event = controller.read(2)[0]
    assert event.title == "title_two"
    assert event.supporter_id == 3

    with pytest.raises(
            AuthorizationDenied,
            match=r"Permission error \(ABAC\) in "
                  r"\(\(not event_has_support and "
                  r"is_event_associated_salesman\) or "
                  r"is_event_associated_support\)"):
        controller.update(2, **data)


def test_support_can_update_his_event(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_support):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"title": "new_title"}
    contract = controller.read(2)[0]
    assert contract.title == "title_two"
    assert contract.supporter_id == 3

    controller.update(2, **data)

    contract = controller.read(2)[0]
    assert contract.title == "new_title"


def test_support_cant_update_other_events(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_support):
    controller = EventManager(EventService(in_memory_uow()))
    data = {"title": "new_title"}
    contract = controller.read(3)[0]
    assert contract.title == "title_thr"
    assert contract.supporter_id is None

    with pytest.raises(
            AuthorizationDenied,
            match=r"Permission error \(ABAC\) in "
                  r"\(\(not event_has_support and "
                  r"is_event_associated_salesman\) or "
                  r"is_event_associated_support\)"):
        controller.update(3, **data)


def test_manager_can_delete_any_event(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    list_event = controller.read()
    assert len(list_event) == 4

    controller.delete(2)

    list_event = controller.read()
    assert len(list_event) == 3


def test_associated_salesman_can_delete_event_without_support(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_sales):
    controller = EventManager(EventService(in_memory_uow()))
    list_event = controller.read()
    assert len(list_event) == 4

    controller.delete(3)

    list_event = controller.read()
    assert len(list_event) == 3


def test_manager_can_assign_support_to_event(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    event = controller.read(3)[0]
    assert event.supporter_id is None

    controller.change_support(pk=3, support_id=3)

    event = controller.read(3)[0]
    assert event.supporter_id == 3


def test_manager_cant_assign_sales_to_event(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    event = controller.read(3)[0]
    assert event.supporter_id is None

    with pytest.raises(EventServiceError,
                       match="Can only assign supports to event"):
        controller.change_support(pk=3, support_id=2)


def test_manager_can_modify_event_support(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    event = controller.read(2)[0]
    assert event.supporter_id == 3

    controller.change_support(pk=2, support_id=4)

    event = controller.read(2)[0]
    assert event.supporter_id == 4


def test_manager_cant_assign_sales_as_event_support(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    event = controller.read(2)[0]
    assert event.supporter_id == 3

    with pytest.raises(EventServiceError,
                       match="Can only assign supports to event"):
        controller.change_support(pk=3, support_id=2)


def test_manager_can_unassign_support_from_event(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    event = controller.read(2)[0]
    assert event.supporter_id == 3

    controller.change_support(pk=2, unassign_flag=True)

    event = controller.read(2)[0]
    assert event.supporter_id is None


def test_user_associated_events(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_support):
    controller = EventManager(EventService(in_memory_uow()))
    events = controller.user_associated_resource(filters=None, sort=None)
    assert len(events) == 2
    assert events[0].id == 1
    assert events[1].id == 2


def test_unassigned_events(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    events = controller.unassigned_events(filters=None, sort=None)
    assert len(events) == 2
    assert events[0].id == 3
    assert events[1].id == 4


def test_orphan_events(
        in_memory_uow, init_db_table_collaborator, init_db_table_client,
        init_db_table_contract, init_db_table_event,
        bypass_permission_manager):
    controller = EventManager(EventService(in_memory_uow()))
    events = controller.orphan_events(filters=None, sort=None)
    assert len(events) == 1
    assert events[0].id == 4
