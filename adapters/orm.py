from sqlalchemy import (
    Table, Column, Boolean, Integer, String, ForeignKey, DateTime, Float, Text)
from sqlalchemy.orm import registry

from domain.model import AuthUser, Role, Collaborator, Client, Contract, Event


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
           unique=True, nullable=False),
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
        },
    )


def start_role_mapper():
    mapper_registry.map_imperatively(
        Role,
        role_table,
        properties={
            "id": role_table.c.role_id,
        },
    )


def start_collaborator_mapper():
    mapper_registry.map_imperatively(
        Collaborator,
        collaborator_table,
        properties={
            "id": collaborator_table.c.collaborator_id,
        },
    )


def start_client_mapper():
    mapper_registry.map_imperatively(
        Client,
        client_table,
        properties={
            "id": client_table.c.client_id,
        },
    )


def start_contract_mapper():
    mapper_registry.map_imperatively(
        Contract,
        contract_table,
        properties={
            "id": contract_table.c.contract_id,
        },
    )


def start_event_mapper():
    mapper_registry.map_imperatively(
        Event,
        event_table,
        properties={
            "id": event_table.c.event_id,
        },
    )


def start_mappers():
    start_user_mapper()
    start_role_mapper()
    start_collaborator_mapper()
    start_client_mapper()
    start_contract_mapper()
    start_event_mapper()
