"""Data Transfer Object (DTO) classes used to expose a safe, immutable
and serializable content of domain entities.

Classes
    AuthUserDTO
    CollaboratorDTO
    ClientDTO
    ContractDTO
    EventDTO
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AuthUserDTO:
    """Immutable, read-only object representation of an authenticated
    user.

    Attributes
        id (int): Primary key of the user.
        username (str): Login name of the user.
    """
    id: int | None = None
    username: str | None = None

    @classmethod
    def from_domain(cls, auth_user):
        """Factory to create an instance from a domain model 'AuthUser'.

        Args
            auth_user (AuthUser): Authenticated user object.

        Returns
            AuthUserDTO: DTO containing safe user data.
        """
        return cls(
            id=auth_user.id,
            username=auth_user.username,
        )


@dataclass(frozen=True, slots=True)
class CollaboratorDTO:
    """Convert a domain model 'Collaborator' into a safe to expose
    dataclass.

    Attributes
        id (int): Primary key of the collaborator.
        last_name (str): Last name of the collaborator.
        first_name (str): First name of the collaborator.
        email (str): Email address of the collaborator.
        phone_number (str): Phone number of the collaborator.
        role (str): Role title of the collaborator.
        user_id (int): Primary key of the associated user account.
    """
    id: int | None = None
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    role: str | None = None
    user_id: int | None = None

    @classmethod
    def from_domain(cls, collaborator):
        """Factory to create an instance from a domain model
        'Collaborator'.
        Factory call a Role.name to return the string associated with
        the role.

        Args
            collaborator (Collaborator): Collaborator object.

        Returns
            CollaboratorDTO: Dataclass exposing limited collaborator
                data.
        """
        return cls(
            id=collaborator.id,
            last_name=collaborator.last_name,
            first_name=collaborator.first_name,
            email=collaborator.email,
            phone_number=collaborator.phone_number,
            role=collaborator.role.name,
            user_id=collaborator.user_id,
        )


@dataclass(frozen=True, slots=True)
class ClientDTO:
    """Convert a domain model 'Client' into a safe to expose dataclass.

    Attributes
        id (int): Primary key of the client.
        last_name (str): Last name of the client.
        first_name (str): First name of the client.
        email (str): Email address of the client.
        phone_number (str): Phone number of the client.
        company (str): Company associated with the client.
        created_at (datetime): Date and time the client was created.
        updated_at (datetime): Date and time the client was last
            updated.
        salesman_id (int): Primary key of the associated salesman.
    """
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
        """Factory to create an instance from a domain model 'Client'.

        Args
            client (Client): Client object.

        Returns
            ClientDTO: Dataclass exposing limited client data.
        """
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


@dataclass(frozen=True, slots=True)
class ContractDTO:
    """Convert a domain model 'Contract' into a safe to expose
    dataclass.

    Attributes
        id (int): Primary key of the contract.
        total_amount (float): Total amount to pay.
        due_amount (float): Remaining amount to pay.
        created_at (datetime): Date and time the contract was created.
        signed (bool): Whether the contract was signed. True is signed.
        client_id (int): Primary key of the associated client.
    """
    id: int | None = None
    total_amount: float | None = None
    due_amount: float | None = None
    created_at: datetime | None = None
    signed: bool | None = None
    client_id: int | None = None

    @classmethod
    def from_domain(cls, contract):
        """Factory to create an instance from a domain model 'Contract'.

        Args
            contract (Contract): Contract object.

        Returns
            ContractDTO: Dataclass exposing limited contract data.
        """
        return cls(
            id=contract.id,
            total_amount=contract.total_amount,
            due_amount=contract.calculate_due_amount(),
            created_at=contract.created_at,
            signed=contract.signed,
            client_id=contract.client_id,
        )


@dataclass(frozen=True, slots=True)
class EventDTO:
    """Convert a domain model 'Event' into a safe to expose dataclass.

    Attributes
        id (int): Primary key of the event.
        title (str): Title of the event.
        start_time (datetime): Date and time the event start.
        end_time (datetime): Date and time the event end.
        location (str): Location of the event.
        attendee (int): Number of attendees in the event.
        notes (str): Notes about the event.
        supporter_id (int): Primary key of the associated supporter.
        contract_id (int): Primary key of the associated contract.
    """
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
        """Factory to create an instance from a domain model 'Event'.

        Args
            event (Event): Event object.

        Returns
            EventDTO: Dataclass exposing limited event data.
        """
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
