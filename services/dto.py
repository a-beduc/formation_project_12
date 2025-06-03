from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthUserDTO:
    id: int | None = None
    username: str | None = None

    @classmethod
    def from_domain(cls, auth_user):
        return cls(
            id=auth_user.id,
            username=auth_user.username,
        )


@dataclass
class CollaboratorDTO:
    id: int | None = None
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    role_id: int | None = None
    user_id: int | None = None

    @classmethod
    def from_domain(cls, collaborator):
        return cls(
            id=collaborator.id,
            last_name=collaborator.last_name,
            first_name=collaborator.first_name,
            email=collaborator.email,
            phone_number=collaborator.phone_number,
            role_id=collaborator.role,
            user_id=collaborator.user_id,
        )


@dataclass
class ClientDTO:
    id: int | None = None
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    company: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    salesman_id: int | None = None

    @classmethod
    def from_domain(cls, client):
        return cls(
            id=client.id,
            last_name=client.last_name,
            first_name=client.first_name,
            email=client.email,
            phone_number=client.phone_number,
            company=client.company,
            created_at=client.created_at,
            updated_at=client.updated_at,
            salesman_id=client.salesman_id,
        )


@dataclass
class ContractDTO:
    id: int | None = None
    total_amount: float | None = None
    due_amount: float | None = None
    created_at: datetime | None = None
    signed: bool | None = None
    client_id: int | None = None

    @classmethod
    def from_domain(cls, contract):
        return cls(
            id=contract.id,
            total_amount=contract.total_amount,
            due_amount=contract.calculate_due_amount(),
            created_at=contract.created_at,
            signed=contract.signed,
            client_id=contract.client_id,
        )


@dataclass
class EventDTO:
    id: int | None = None
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    attendee: int | None = None
    notes: str | None = None
    supporter_id: int | None = None
    contract_id: int | None = None

    @classmethod
    def from_domain(cls, event):
        return cls(
            id=event.id,
            title=event.title,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            attendee=event.attendee,
            notes=event.notes,
            supporter_id=event.supporter_id,
            contract_id=event.contract_id,
        )