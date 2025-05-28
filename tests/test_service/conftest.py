import pytest
from adapters.repositories import (AbstractRepository,
                                   AbstractContractRepository)
from domain.model import Client
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

    def _filter(self, **filters):
        return [obj for obj in self._store.values()
                if all(getattr(obj, attr, None) == value
                for attr, value in filters.items())
                ]

    def _filter_one(self, **filters):
        return next(
            (obj for obj in self._store.values()
             if all(getattr(obj, attr, None) == value
             for attr, value in filters.items())),
            None
        )


class FakeClientRepository(FakeRepository, AbstractContractRepository):
    def get_client_from_contract(self, salesman_id):
        return [client for client in self._store.values() if
                isinstance(client, Client) and
                client.salesman_id == salesman_id]


# init empty interface, add tuples of objects to FakeRepos to init with datas
class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.commited = False
        self.users = FakeRepository()
        self.collaborators = FakeRepository()
        self.roles = FakeRepository()
        self.clients = FakeClientRepository()
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
