"""Map SQL tables to domain models using SQLAlchemy 2.x imperative
mapping. We purposely use imperative (classical) mapping instead of
declarative so that our entities does not depend on SQLAlchemy classes.

Functions
    start_user_mapper           # Map class 'AuthUser'
    start_collaborator_mapper   # Map class 'Collaborator'
    start_client_mapper         # Map class 'Client'
    start_contract_mapper       # Map class 'Contract'
    start_event_mapper          # Map class 'Event'
    start_mappers               # Initialize all mappings

References
    * imperative mapping.
https://docs.sqlalchemy.org/en/21/orm/mapping_styles.html#orm-imperative-mapping
https://getdocs.org/Sqlalchemy/docs/latest/orm/mapping_styles#imperative-mapping-with-dataclasses-and-attrs
    * synonym.
https://docs.sqlalchemy.org/en/20/orm/mapped_attributes.html#codecell15
    * column_property
https://docs.sqlalchemy.org/en/21/orm/mapped_sql_expr.html#using-column-property
"""
from sqlalchemy import Table, Column, Boolean, Integer, String, ForeignKey, \
    DateTime, Float, Text
from sqlalchemy.orm import registry, relationship, synonym, column_property

from ee_crm.domain.model import AuthUser, Collaborator, Client, Contract, Event

mapper_registry = registry()

user_table = Table(
    'users',
    mapper_registry.metadata,
    Column('user_id', Integer, primary_key=True,
           nullable=False, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    schema='auth'
)

role_table = Table(
    'role',
    mapper_registry.metadata,
    Column('role_id', Integer, primary_key=True,
           nullable=False, autoincrement=True),
    Column('role', String(20), unique=True, nullable=False),
    schema='crm'
)

collaborator_table = Table(
    'collaborator',
    mapper_registry.metadata,
    Column('collaborator_id', Integer, primary_key=True,
           nullable=False, autoincrement=True),
    Column('last_name', String(255)),
    Column('first_name', String(255)),
    Column('email', String(255), unique=True),
    Column('phone_number', String(20)),
    Column('role_id', Integer, ForeignKey('crm.role.role_id')),
    Column('user_id', Integer, ForeignKey('auth.users.user_id'),
           unique=True),
    schema='crm'
)

client_table = Table(
    'client',
    mapper_registry.metadata,
    Column('client_id', Integer, primary_key=True,
           nullable=False, autoincrement=True),
    Column('last_name', String(255)),
    Column('first_name', String(255)),
    Column('email', String(255)),
    Column('phone_number', String(20)),
    Column('company', String(255)),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
    Column('salesman_id', Integer,
           ForeignKey('crm.collaborator.collaborator_id')),
    schema='crm'
)

contract_table = Table(
    'contract',
    mapper_registry.metadata,
    Column('contract_id', Integer, primary_key=True,
           nullable=False, autoincrement=True),
    Column('total_amount', Float),
    Column('paid_amount', Float),
    Column('created_at', DateTime(timezone=True)),
    Column('signed', Boolean, nullable=False, default=False),
    Column('client_id', Integer, ForeignKey('crm.client.client_id')),
    schema='crm'
)

event_table = Table(
    'event',
    mapper_registry.metadata,
    Column('event_id', Integer, primary_key=True,
           nullable=False, autoincrement=True),
    Column('title', String(255)),
    Column('start_time', DateTime(timezone=True)),
    Column('end_time', DateTime(timezone=True)),
    Column('location', String(255)),
    Column('attendee', Integer),
    Column('notes', Text),
    Column('supporter_id', Integer,
           ForeignKey('crm.collaborator.collaborator_id')),
    Column('contract_id', Integer,
           ForeignKey('crm.contract.contract_id')),
    schema='crm'
)


def start_user_mapper():
    """Map the AuthUser entity.

    columns > attributes:
        user_table.c.user_id    -> AuthUser.id
        user_table.c.username   -> AuthUser._username
        user_table.c.password   -> AuthUser._password

    relationships:
        'collaborator' back_populate create an attribute AuthUser.collaborator
            -> (Collaborator)
    """
    mapper_registry.map_imperatively(
        AuthUser,
        user_table,
        properties={
            "id": user_table.c.user_id,
            "_username": user_table.c.username,
            "_password": user_table.c.password,
            "collaborator": relationship(
                Collaborator,
                back_populates="user",
                uselist=False,
            )
        },
    )


def start_collaborator_mapper():
    """Map the Collaborator entity.

    columns -> attributes:
        collaborator_table.c.collaborator_id    -> Collaborator.id
        collaborator_table.c.role_id            -> Collaborator._role_id
        collaborator_table.c.user_id            -> Collaborator._user_id

    relationships:
        'user' back_populate create an attribute Collaborator.user
            -> (AuthUser)
        'clients' back_populate create an attribute Collaborator.clients
            -> (list(Client))
        'events' back_populate create an attribute Collaborator.events
            -> (list(Event))
    """
    mapper_registry.map_imperatively(
        Collaborator,
        collaborator_table,
        properties={
            "id": collaborator_table.c.collaborator_id,
            "_role_id": collaborator_table.c.role_id,
            "_user_id": collaborator_table.c.user_id,
            "user": relationship(
                AuthUser,
                back_populates="collaborator",
                uselist=False
            ),
            "clients": relationship(
                Client,
                back_populates="salesman",
                order_by=client_table.c.client_id
            ),
            "events": relationship(
                Event,
                back_populates="supporter",
                order_by=event_table.c.event_id
            )
        },
    )


def start_client_mapper():
    """Map the Client entity.

    columns -> attributes:
        client_table.c.client_id    -> Client.id
        client_table.c.created_at   -> Client._created_at
        client_table.c.updated_at   -> Client._updated_at
        client_table.c.salesman_id  -> Client._salesman_id

    synonym:
        Allows use of Client.salesman_id_sql in SQLAlchemy queries
        even if mapped data is on attribute Client._salesman_id.

    relationships:
        'salesman' back_populate create an attribute Client.salesman
            -> (Collaborator)
        'contracts' back_populate create an attribute Client.contracts
            -> (list(Contract))
    """
    mapper_registry.map_imperatively(
        Client,
        client_table,
        properties={
            "id": client_table.c.client_id,
            "_created_at": client_table.c.created_at,
            "_updated_at": client_table.c.updated_at,
            "_salesman_id": client_table.c.salesman_id,
            "salesman_id_sql": synonym("_salesman_id"),
            "salesman": relationship(
                Collaborator,
                back_populates="clients",
                uselist=False
            ),
            "contracts": relationship(
                Contract,
                back_populates="client",
                order_by=contract_table.c.contract_id
            )
        },
    )


def start_contract_mapper():
    """Map the Contract entity.

    columns -> attributes:
        contract_table.c.contract_id    -> Contract.id
        contract_table.c.total_amount   -> Contract._total_amount
        contract_table.c.paid_amount    -> Contract._paid_amount
        contract_table.c.signed         -> Contract._signed
        contract_table.c.client_id      -> Contract._client_id

    synonym:
        Allows use of Contract.signed_sql in SQLAlchemy queries even if
        mapped data is on attribute Client._signed.

    column_property:
        Allows use of a func due_amount_sql in SQLAlchemy queries to
        interrogate a dynamically calculated value.

    relationships:
        'client' back_populate create an attribute Contract.client
            -> (Client)
        'event' back_populate create an attribute Contract.event
            -> (Event)
    """
    mapper_registry.map_imperatively(
        Contract,
        contract_table,
        properties={
            "id": contract_table.c.contract_id,
            "_total_amount": contract_table.c.total_amount,
            "_paid_amount": contract_table.c.paid_amount,
            "_signed": contract_table.c.signed,
            "signed_sql": synonym("_signed"),
            "_client_id": contract_table.c.client_id,
            "due_amount_sql": column_property(contract_table.c.total_amount -
                                              contract_table.c.paid_amount),
            "client": relationship(
                Client,
                back_populates="contracts",
                uselist=False
            ),
            "event": relationship(
                Event,
                back_populates="contract",
                uselist=False
            )
        },
    )


def start_event_mapper():
    """Map the Event entity.

    columns -> attributes:
        event_table.c.event_id      -> Event.id
        event_table.c.contract_id   -> Event._contract_id

    relationships:
        'contract' back_populate create an attribute Event.contract
            -> (Contract)
        'supporter' back_populate create an attribute Event.supporter
            -> (Collaborator)
    """
    mapper_registry.map_imperatively(
        Event,
        event_table,
        properties={
            "id": event_table.c.event_id,
            "_contract_id": event_table.c.contract_id,
            "contract": relationship(
                Contract,
                back_populates="event",
                uselist=False
            ),
            "supporter": relationship(
                Collaborator,
                back_populates="events",
                uselist=False
            )
        },
    )


def start_mappers():
    """Initialize the mappers. Need to be called when starting up the
    application.
    """
    start_user_mapper()
    start_collaborator_mapper()
    start_client_mapper()
    start_contract_mapper()
    start_event_mapper()
