"""Integration tests for the SqlAlchemyUnitOfWork.

The tests assert that the Unit Of Work (uow) behave as expected when
handling transaction boundaries (commit, rollback, exit/error).

Fixtures
    session_factory
        SQLAlchemy sessionmaker object bound to the in-memory
        test SQLite database.
    init_db_table_users
        create and populate the table linked to the AuthUser model.
"""
import pytest

from ee_crm.domain.model import AuthUser
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork


def test_uow_can_retrieve_user(session_factory, init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user_one = uow.users.get(1)
        assert user_one.username == 'user_one'


def test_uow_can_retrieve_a_user_modify_it_and_save_it(session_factory,
                                                       init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user_one = uow.users.get(1)
        user_one.username = 'new_name'
        uow.commit()
        assert uow.users.get(1).username == 'new_name'


def test_uow_can_save_a_user(session_factory, init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user = AuthUser(_username='user_fiv', _password='Password5')
        uow.users.add(user)
        uow.commit()

    with uow:
        assert uow.users.get(5).username == 'user_fiv'


def test_uow_can_delete_a_user(session_factory, init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        uow.users.delete(1)
        uow.commit()

    with uow:
        assert uow.users.get(1) is None


def test_uow_add_without_commit_trigger_rollback(session_factory,
                                                 init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user = AuthUser(_username='user_fiv', _password='Password5')
        uow.users.add(user)

    with uow:
        assert uow.users.get(5) is None


def test_uow_modifying_without_commit_trigger_rollback(session_factory,
                                                       init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user_one = uow.users.get(1)
        user_one.username = 'new_name'

    with uow:
        assert uow.users.get(1).username == "user_one"


def test_uow_deleting_without_commit_trigger_rollback(session_factory,
                                                      init_db_table_users):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        uow.users.delete(1)

    with uow:
        assert uow.users.get(1).username == "user_one"


def test_uow_rollback_on_error(session_factory, init_db_table_users):
    """Verify that rollback works as expected when an error occurs
    before committing."""
    class MyException(Exception):
        pass

    uow = SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            user = AuthUser(_username='user_fiv', _password='Password5')
            uow.users.add(user)
            raise MyException()

    with uow:
        assert uow.users.get(5) is None
