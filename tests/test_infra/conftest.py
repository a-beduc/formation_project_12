import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers

from adapters.orm import (user_table, role_table, collaborator_table,
                          client_table, contract_table, event_table)
from adapters.orm import mapper_registry, start_user_mapper


@pytest.fixture(scope="session")
def db_engine():
    # remove the schema because SQLite doesn't accept 'auth.users' only 'users'
    user_table.schema = None
    role_table.schema = None
    collaborator_table.schema = None
    client_table.schema = None
    contract_table.schema = None
    event_table.schema = None

    engine = create_engine('sqlite:///:memory:')
    mapper_registry.metadata.create_all(engine)
    yield engine


@pytest.fixture
def session(db_engine):
    start_user_mapper()
    with db_engine.connect() as connection:
        transaction_savepoint = connection.begin()

        with sessionmaker(bind=connection)() as session:
            yield session

        transaction_savepoint.rollback()
    clear_mappers()


@pytest.fixture
def init_db_table_users(session):
    stmt = text(
        "INSERT INTO users (username, password) VALUES "
        "('user_one', 'password_one'), "
        "('user_two', 'password_two'), "
        "('user_three', 'password_three')")
    session.execute(stmt)
    session.commit()
