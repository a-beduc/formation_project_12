import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers

from adapters.orm import (user_table, role_table, collaborator_table,
                          client_table, contract_table, event_table)
from adapters.orm import mapper_registry, start_mappers


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
    start_mappers()
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
        "('user_thr', 'password_thr')"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_role(session):
    stmt = text(
        "INSERT INTO role (role) VALUES "
        "('Deactivated'), "
        "('Admin'), "
        "('Management'), "
        "('Sales'), "
        "('Support')"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_collaborator(session):
    stmt = text(
        "INSERT INTO collaborator (last_name, first_name, email, phone_number, role_id, user_id) VALUES "
        "('col_ln_one', 'col_fn_one', 'col_email@one', '0000000001', '3', '1'), "
        "('col_ln_two', 'col_fn_two', 'col_email@two', '0000000002', '4', '2'), "
        "('col_ln_thr', 'col_fn_thr', 'col_email@thr', '0000000003', '5', '3')"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_client(session):
    stmt = text(
        "INSERT INTO client (last_name, first_name, email, phone_number, company, created_at, updated_at, salesman_id) VALUES "
        "('cli_ln_one', 'cli_fn_one', 'cli_email@one', '0000000001', 'comp_one', '2025-01-01 00:00:01', '2025-02-01 00:00:01', '1'), "
        "('cli_ln_two', 'cli_fn_two', 'cli_email@two', '0000000002', 'comp_two', '2025-01-01 00:00:02', '2025-02-01 00:00:02', '2'), "
        "('cli_ln_thr', 'cli_fn_thr', 'cli_email@thr', '0000000003', 'comp_thr', '2025-01-01 00:00:03', '2025-02-01 00:00:03', '3')"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_contract(session):
    stmt = text(
        "INSERT INTO contract (total_amount, paid_amount, created_at, signed, client_id) VALUES "
        "(100.0, 10.0, '2025-05-01 00:00:01', true, 1), "
        "(100.0, 20.0, '2025-05-02 00:00:02', true, 2), "
        "(100.0, 0.0, '2025-05-03 00:00:03', false, 3)"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_event(session):
    stmt = text(
        "INSERT INTO event (title, start_time, end_time, location, notes, supporter_id, contract_id) VALUES "
        "('title_one', '2025-06-01 00:00:01', '2025-06-01 01:00:01', 'location_one', 'notes_one', 3, 1), "
        "('title_two', '2025-06-01 00:00:01', '2025-06-01 01:00:01', 'location_two', 'notes_two', 3, 3)"
    )
    session.execute(stmt)
    session.commit()
