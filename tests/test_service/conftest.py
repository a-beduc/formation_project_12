import pytest
from ee_crm.adapters.repositories import (AbstractRepository,
                                          AbstractContractRepository)
from ee_crm.domain.model import Client
from ee_crm.services.unit_of_work import AbstractUnitOfWork


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

    def _list(self, sort=None):
        storage = list(self._store.values())
        if sort is not None:
            reversed_storage = storage[::-1]
            for sort_tuple in reversed_storage:
                storage = sorted(storage,
                                 key=lambda x: getattr(x, sort_tuple[0]),
                                 reverse=sort_tuple[1])
        return storage

    def _filter(self, sort=None, **filters):
        filtered = [obj for obj in self._store.values()
                    if all(getattr(obj, attr, None) == value
                    for attr, value in filters.items())]
        if sort is not None:
            reversed_storage = filtered[::-1]
            for sort_tuple in reversed_storage:
                filtered = sorted(filtered,
                                  key=lambda x: getattr(x, sort_tuple[0]),
                                  reverse=sort_tuple[1])
        return [obj for obj in self._store.values()
                if all(getattr(obj, attr, None) == value
                for attr, value in filters.items())]

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
