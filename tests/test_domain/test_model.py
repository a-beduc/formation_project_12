# ask help for how to mock datetime later, a solution could be to add a _now()
# in the model package and mock the _now() to circumvent the datetime mocking

import pytest

import domain.model as dm


def test_auth_user_builder_success():
    user = dm.AuthUser.builder(username="user_one", plain_password="Password1")

    assert isinstance(user, dm.AuthUser)
    assert user.username == "user_one"
    user.verify_password("Password1")

    with pytest.raises(dm.AuthUserError, match="Password mismatch"):
        user.verify_password("wrong_password")


def test_collaborator_builder_success():
    collaborator = dm.Collaborator.builder(last_name="last_name",
                                           first_name="first_name",
                                           user_id=1)

    assert isinstance(collaborator, dm.Collaborator)
    assert collaborator.id is None
    assert collaborator.last_name == "last_name"
    assert collaborator.first_name == "first_name"
    assert collaborator.email is None
    assert collaborator.phone_number is None
    assert collaborator.role is dm.Role.DEACTIVATED
    assert collaborator.user_id == 1


def test_client_builder_success():
    client = dm.Client.builder(last_name="last_name",
                               first_name="first_name",
                               salesman_id=1)

    assert isinstance(client, dm.Client)
    assert client.last_name == "last_name"
    assert client.first_name == "first_name"
    assert client.email is None
    assert client.phone_number is None
    assert client.company is None
    assert client.salesman_id == 1


def test_contract_builder_success():
    contract = dm.Contract.builder(total_amount=100, client_id=1)

    assert isinstance(contract, dm.Contract)
    assert contract.total_amount == 100.00
    assert contract.paid_amount == 0.00
    assert contract.signed is False
    assert contract.client_id == 1


def test_event_builder_success():
    event = dm.Event.builder(title="new event", contract_id=1)

    assert isinstance(event, dm.Event)
    assert event.title == "new event"
    assert event.start_time is None
    assert event.end_time is None
    assert event.location is None
    assert event.attendee is None
    assert event.notes is None
    assert event.supporter_id is None
    assert event.contract_id == 1
