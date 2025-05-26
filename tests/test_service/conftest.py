import pytest
from adapters.repositories import (AbstractRepository, AbstractUserRepository,
                                   AbstractCollaboratorRepository)
from domain.model import AuthUser, Collaborator
from services.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
    def __init__(self, init=()):
        super().__init__()
        self._store = {}
        self._pk = 0
        for obj in init:
            self._add(obj)

    def _add(self, model_obj):
        if getattr(model_obj, "id", None) is None:
            self._pk += 1
            model_obj.id = self._pk
        self._store[model_obj.id] = model_obj

    def _get(self, obj_pk):
        return self._store.get(obj_pk, None)

    def _delete(self, obj_pk):
        self._store.pop(obj_pk, None)

    def _list(self):
        return list(self._store.values())

    def _update(self, model_obj):
        if getattr(model_obj, "id", None) is None:
            raise ValueError('The object id is not found')
        self._store[model_obj.id] = model_obj


class FakeUserRepository(FakeRepository, AbstractUserRepository):
    def get_by_username(self, username):
        return next(
            (user for user in self._store.values() if
             isinstance(user, AuthUser) and user.username == username), None
        )


class FakeCollaboratorRepository(FakeRepository,
                                 AbstractCollaboratorRepository):
    def get_by_user_id(self, user_id):
        return next(
            (collaborator for collaborator in self._store.values() if
             isinstance(collaborator, Collaborator) and
             collaborator.user_id == user_id),
            None)

    def filter_by_role(self, role_id):
        return [collaborator for collaborator in self._store.values() if
                isinstance(collaborator, Collaborator) and
                collaborator.role_id == role_id]


# init empty interface, add tuples of objects to FakeRepos to init with datas
class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.commited = False
        self.users = FakeUserRepository()
        self.collaborators = FakeCollaboratorRepository()
        self.roles = FakeRepository()
        self.clients = FakeRepository()
        self.contracts = FakeRepository()
        self.events = FakeRepository()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def rollback(self):
        pass

    def _commit(self):
        self.commited = True


@pytest.fixture(scope='function')
def uow():
    return FakeUnitOfWork()
