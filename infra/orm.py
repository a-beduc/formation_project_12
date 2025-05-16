from sqlalchemy import Table, Column, Boolean, Integer, String
from sqlalchemy.orm import registry

from domain.model import AuthUser


mapper_registry = registry()

user_table = Table(
    'users',
    mapper_registry.metadata,
    Column('user_id', Integer, primary_key=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    Column('superuser', Boolean, nullable=False, default=False),
    schema='auth'
)


def start_mappers():
    mapper_registry.map_imperatively(
        AuthUser,
        user_table,
        properties={
            "id": user_table.c.user_id,
        },
    )
