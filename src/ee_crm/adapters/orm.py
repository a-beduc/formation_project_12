from sqlalchemy import (
    Table, Column, Boolean, Integer, String, ForeignKey, DateTime, Float, Text)
from sqlalchemy.orm import registry, relationship

from ee_crm.domain.model import AuthUser, Collaborator, Client, Contract, Event


mapper_registry = registry()

user_table = Table(
    'users',
    mapper_registry.metadata,
    Column('user_id', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    schema='auth'
)

role_table = Table(
    'role',
    mapper_registry.metadata,
    Column('role_id', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('role', String(20), unique=True, nullable=False),
    schema='crm'
)

collaborator_table = Table(
    'collaborator',
    mapper_registry.metadata,
    Column('collaborator_id', Integer, primary_key=True, nullable=False, autoincrement=True),
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
    Column('client_id', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('last_name', String(255)),
    Column('first_name', String(255)),
    Column('email', String(255)),
    Column('phone_number', String(20)),
    Column('company', String(255)),
    Column('created_at', DateTime(timezone=True)),
    Column('updated_at', DateTime(timezone=True)),
    Column('salesman_id', Integer, ForeignKey('crm.collaborator.collaborator_id')),
    schema='crm'
)

contract_table = Table(
    'contract',
    mapper_registry.metadata,
    Column('contract_id', Integer, primary_key=True, nullable=False, autoincrement=True),
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
    Column('event_id', Integer, primary_key=True, nullable=False, autoincrement=True),
    Column('title', String(255)),
    Column('start_time', DateTime(timezone=True)),
    Column('end_time', DateTime(timezone=True)),
    Column('location', String(255)),
    Column('attendee', Integer),
    Column('notes', Text),
    Column('supporter_id', Integer, ForeignKey('crm.collaborator.collaborator_id')),
    Column('contract_id', Integer, ForeignKey('crm.contract.contract_id')),
    schema='crm'
)


def start_user_mapper():
    mapper_registry.map_imperatively(
        AuthUser,
        user_table,
        properties={
            "id": user_table.c.user_id,
            "_username":user_table.c.username,
            "_password": user_table.c.password,
            "collaborator": relationship(
                Collaborator,
                back_populates="user",
                uselist=False,
            )
        },
    )


def start_collaborator_mapper():
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
    mapper_registry.map_imperatively(
        Client,
        client_table,
        properties={
            "id": client_table.c.client_id,
            "_created_at": client_table.c.created_at,
            "_updated_at": client_table.c.updated_at,
            "_salesman_id": client_table.c.salesman_id,
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
    mapper_registry.map_imperatively(
        Contract,
        contract_table,
        properties={
            "id": contract_table.c.contract_id,
            "_total_amount": contract_table.c.total_amount,
            "_paid_amount": contract_table.c.paid_amount,
            "_signed": contract_table.c.signed,
            "_client_id": contract_table.c.client_id,
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
    start_user_mapper()
    start_collaborator_mapper()
    start_client_mapper()
    start_contract_mapper()
    start_event_mapper()
