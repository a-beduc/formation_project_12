from abc import ABC, abstractmethod
from domain.model import AuthUser, Collaborator, Client, Contract, Event


class AbstractRepository(ABC):

    def add(self, model_obj):
        self._add(model_obj)

    def get(self, obj_pk):
        return self._get(obj_pk)

    def delete(self, obj_pk):
        self._delete(obj_pk)

    def list(self):
        return self._list()

    def filter(self, **filters):
        return self._filter(**filters)

    def filter_one(self, **filters):
        return self._filter_one(**filters)

    @abstractmethod
    def _add(self, model_obj):
        raise NotImplementedError

    @abstractmethod
    def _get(self, obj_pk):
        raise NotImplementedError

    @abstractmethod
    def _delete(self, obj_pk):
        raise NotImplementedError

    @abstractmethod
    def _list(self):
        raise NotImplementedError

    @abstractmethod
    def _filter(self, **filters):
        raise NotImplementedError

    @abstractmethod
    def _filter_one(self, **filters):
        raise NotImplementedError


class AbstractContractRepository(AbstractRepository):
    @abstractmethod
    def get_client_from_contract(self, contract_id):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    model_cls = None

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _translate_filters(self, filters):
        aliases = getattr(self.model_cls, "_private_aliases", {})
        return {aliases.get(k, k): v for k, v in filters.items()}

    def _add(self, model_obj):
        self.session.add(model_obj)

    def _get(self, obj_pk):
        return self.session.get(self.model_cls, obj_pk)

    def _delete(self, obj_pk):
        obj = self.session.get(self.model_cls, obj_pk)
        self.session.delete(obj)

    def _list(self):
        return self.session.query(self.model_cls).all()

    def _filter(self, **filters):
        orm_filters = self._translate_filters(filters)
        return self.session.query(self.model_cls).filter_by(**orm_filters).all()

    def _filter_one(self, **filters):
        orm_filters = self._translate_filters(filters)
        return (self.session.query(self.model_cls).filter_by(**orm_filters).
                one_or_none())


class SqlAlchemyUserRepository(SqlAlchemyRepository):
    model_cls = AuthUser


class SqlAlchemyCollaboratorRepository(SqlAlchemyRepository):
    model_cls = Collaborator


class SqlAlchemyClientRepository(SqlAlchemyRepository):
    model_cls = Client


class SqlAlchemyContractRepository(SqlAlchemyRepository,
                                   AbstractContractRepository):
    model_cls = Contract

    def get_client_from_contract(self, contract_id):
        contract = self._get(contract_id)
        return self.session.query(Client).filter_by(
            id=contract.client_id).one_or_none()


class SqlAlchemyEventRepository(SqlAlchemyRepository):
    model_cls = Event
