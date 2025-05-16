import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers

from infra.orm import user_table
from infra.orm import mapper_registry, start_mappers


@pytest.fixture(scope="session")
def in_memory_db():
    user_table.schema = None
    engine = create_engine('sqlite:///:memory:')
    mapper_registry.metadata.create_all(engine)
    yield engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    connection = in_memory_db.connect()
    transaction_savepoint = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction_savepoint.rollback()
    connection.close()
    clear_mappers()


@pytest.fixture
def init_db_table_users(session):
    session.execute(text(
        "INSERT INTO users (username, password, superuser) VALUES "
        "('user_one', 'password_one', false), "
        "('user_two', 'password_two', false), "
        "('user_three', 'password_three', false)")
    ),
    session.commit()
