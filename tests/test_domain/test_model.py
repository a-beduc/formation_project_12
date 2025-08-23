"""Unit tests for ee_crm.domain.model entities

Tests focus on the .builder() factory methods happy paths.
"""
from datetime import datetime, timedelta

import pytest

from ee_crm.domain.model import AuthUser, Collaborator, Contract, Client, \
    Event, Role
from ee_crm.exceptions import AuthUserDomainError


def test_auth_user_builder_success():
    """'AuthUser.builder' should create AuthUser, hash the password and
    allow verification."""
    user = AuthUser.builder(username="user_one", plain_password="Password1")

    assert isinstance(user, AuthUser)
    assert user.username == "user_one"
    user.verify_password("Password1")

    with pytest.raises(AuthUserDomainError, match="Password mismatch"):
        user.verify_password("wrong_password")


def is_recent(time_to_test, time_delta=300):
    """Helper, to test if a given time is in a timeframe off more or
    less than 5 minutes."""
    now = datetime.now()
    delta = timedelta(seconds=time_delta)
    return now - delta <= time_to_test <= now + delta


def test_collaborator_builder_success():
    """'Collaborator.builder' sets default fields correctly."""
    collaborator = Collaborator.builder(last_name="last_name",
                                        first_name="first_name",
                                        user_id=1)

    assert isinstance(collaborator, Collaborator)
    assert collaborator.last_name == "last_name"
    assert collaborator.first_name == "first_name"
    assert collaborator.email is None
    assert collaborator.phone_number is None
    assert collaborator.role is Role.DEACTIVATED
    assert collaborator.user_id == 1


def test_client_builder_success():
    """'Client.builder' sets default fields correctly."""
    client = Client.builder(last_name="last_name",
                            first_name="first_name",
                            salesman_id=1)

    assert isinstance(client, Client)
    assert client.last_name == "last_name"
    assert client.first_name == "first_name"
    assert client.email is None
    assert client.phone_number is None
    assert client.company is None
    assert client.salesman_id == 1

    # verify if created_at and updated_at are not empty and type
    # datetime and verify if it's not older than a few minutes
    assert isinstance(client.created_at, datetime)
    assert isinstance(client.updated_at, datetime)
    assert is_recent(client.created_at)
    assert is_recent(client.updated_at)


def test_contract_builder_success():
    """'Contract.builder' sets default fields correctly."""
    contract = Contract.builder(total_amount=100, client_id=1)

    assert isinstance(contract, Contract)
    assert contract.total_amount == 100.00
    assert contract.paid_amount == 0.00
    assert contract.signed is False
    assert contract.client_id == 1

    # verify if created_at is not empty and type datetime and verify if it's
    # not older than a few minutes
    assert isinstance(contract.created_at, datetime)
    assert is_recent(contract.created_at)


def test_event_builder_success():
    """'Event.builder' sets default fields correctly."""
    event = Event.builder(title="new event", contract_id=1)

    assert isinstance(event, Event)
    assert event.title == "new event"
    assert event.start_time is None
    assert event.end_time is None
    assert event.location is None
    assert event.attendee is None
    assert event.notes is None
    assert event.supporter_id is None
    assert event.contract_id == 1
