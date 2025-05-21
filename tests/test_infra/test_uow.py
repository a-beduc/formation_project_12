import pytest

from services.unit_of_work import SqlAlchemyUnitOfWork
from domain.model import AuthUser


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
        uow.users.update(user_one)
        uow.commit()
        assert uow.users.get(1).username == 'new_name'


def test_uow_can_save_a_user(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user_one = AuthUser(username='user_one', password='password_one')
        uow.users.add(user_one)
        uow.commit()
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        assert uow.users.get(1).username == 'user_one'


def test_uow_modifying_without_commit_trigger_rollback(session_factory):
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        user_one = AuthUser(username='user_one', password='password_one')
        uow.users.add(user_one)
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        assert uow.users.get(1) is None


def test_uow_rollback_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            user = AuthUser(username='user_one', password='Password1')
            uow.users.add(user)
            raise MyException()

    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        assert uow.users.get(1) is None
