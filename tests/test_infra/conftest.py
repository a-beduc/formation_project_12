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
