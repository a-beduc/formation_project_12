import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, clear_mappers

from ee_crm.adapters.orm import (user_table, role_table, collaborator_table,
                                 client_table, contract_table, event_table)
from ee_crm.adapters.orm import mapper_registry, start_mappers


from ee_crm.adapters.repositories import AbstractRepository
from ee_crm.services.unit_of_work import (AbstractUnitOfWork,
                                          SqlAlchemyUnitOfWork)


@pytest.fixture
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
def connection(db_engine):
    start_mappers()
    with db_engine.connect() as connection:
        transaction_savepoint = connection.begin()
        yield connection
        transaction_savepoint.rollback()
    clear_mappers()


# see (https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
# #joining-a-session-into-an-external-transaction-such-as-for-test-suites)
@pytest.fixture
def session_factory(connection):
    return sessionmaker(bind=connection,
                        join_transaction_mode="create_savepoint")


@pytest.fixture
def in_memory_uow(session_factory):
    def factory():
        return SqlAlchemyUnitOfWork(session_factory=session_factory)
    return factory


@pytest.fixture
def session(session_factory):
    with session_factory() as session:
        yield session


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
def init_db_table_collaborator(session):
    stmt = text(
        "INSERT INTO collaborator (last_name, first_name, email, "
        "phone_number, role_id, user_id) VALUES"
        "('col_ln_one', 'col_fn_one', 'col_email@one', '0000000001', '3', "
        "'1'),"
        "('col_ln_two', 'col_fn_two', 'col_email@two', '0000000002', '4', "
        "'2'),"
        "('col_ln_thr', 'col_fn_thr', 'col_email@thr', '0000000003', '5', '3')"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_client(session):
    stmt = text(
        "INSERT INTO client (last_name, first_name, email, phone_number,"
        "company, created_at, updated_at, salesman_id) VALUES"
        "('cli_ln_one', 'cli_fn_one', 'cli_email@one', '0000000001', "
        "'comp_one', '2025-01-01 00:00:01', '2025-02-01 00:00:01', '1'),"
        "('cli_ln_two', 'cli_fn_two', 'cli_email@two', '0000000002', "
        "'comp_two', '2025-01-01 00:00:02', '2025-02-01 00:00:02', '2'),"
        "('cli_ln_thr', 'cli_fn_thr', 'cli_email@thr', '0000000003', "
        "'comp_thr', '2025-01-01 00:00:03', '2025-02-01 00:00:03', '2'),"
        "('cli_ln_fou', 'cli_fn_fou', 'cli_email@fou', '0000000004', "
        "'comp_fou', '2025-01-01 00:00:04', '2025-02-01 00:00:04', NULL)"
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_contract(session):
    stmt = text(
        "INSERT INTO contract (total_amount, paid_amount, created_at, "
        "signed, client_id) VALUES"
        "(100.0, 10.0, '2025-05-01 00:00:01', true, 1), "
        "(100.0, 20.0, '2025-05-02 00:00:02', true, 2), "
        "(100.0, 0.0, '2025-05-03 00:00:03', false, 3), "
        "(100.0, 0.0, '2025-05-04 00:00:04', false, 4), "
        "(100.0, 0.0, '2025-05-05 00:00:05', true, 3) "
    )
    session.execute(stmt)
    session.commit()


@pytest.fixture
def init_db_table_event(session):
    stmt = text(
        "INSERT INTO event (title, start_time, end_time, location, notes, "
        "supporter_id, contract_id) VALUES"
        "('title_one', '2025-06-01 00:00:01', '2025-06-01 01:00:01', "
        "'location_one', 'notes_one', 3, 1),"
        "('title_two', '2025-06-01 00:00:01', '2025-06-01 01:00:01', "
        "'location_two', 'notes_two', 3, 3),"
        "('title_thr', '2025-06-01 00:00:01', '2025-06-01 01:00:01', "
        "'location_thr', 'notes_thr', NULL, 5)"
    )
    session.execute(stmt)
    session.commit()


class FakeRepository(AbstractRepository):
    def __init__(self, init=()):
        super().__init__()
        self._store = {}

        self._pk = 0
        for obj in init:
            self._add(obj)

    @staticmethod
    def _apply_sort(sort, list_to_sort):
        for field, is_desc in sort[::-1]:
            list_to_sort = sorted(list_to_sort,
                                  key=lambda x: getattr(x, field),
                                  reverse=is_desc)
        return list_to_sort

    def _add(self, model_obj):
        if getattr(model_obj, "id", None) is None:
            self._pk += 1
            model_obj.id = self._pk
        self._store[model_obj.id] = model_obj

    def _get(self, obj_pk):
        return self._store.get(obj_pk, None)

    def _delete(self, obj_pk):
        self._store.pop(obj_pk, None)

    def _list(self, sort=None):
        storage = list(self._store.values())
        if sort is not None:
            if sort is not None:
                storage = self._apply_sort(sort, storage)
        return storage

    def _filter(self, sort=None, **filters):
        filtered = [obj for obj in self._store.values()
                    if all(getattr(obj, attr, None) == value
                           for attr, value in filters.items())]
        if sort is not None:
            filtered = self._apply_sort(sort, filtered)
        return filtered

    def _filter_one(self, **filters):
        return next(
            (obj for obj in self._store.values()
             if all(getattr(obj, attr, None) == value
                    for attr, value in filters.items())),
            None
        )


class MockSession:
    def flush(self):
        pass


# init empty interface, add tuples of objects to FakeRepos to init with datas
class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.commited = False
        self.users = FakeRepository()
        self.collaborators = FakeRepository()
        self.clients = FakeRepository()
        self.contracts = FakeRepository()
        self.events = FakeRepository()
        self.session = MockSession()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def rollback(self):
        pass

    def _commit(self):
        self.commited = True


@pytest.fixture(scope='function')
def fake_repo():
    return FakeRepository


@pytest.fixture(scope='function')
def uow():
    return FakeUnitOfWork()
