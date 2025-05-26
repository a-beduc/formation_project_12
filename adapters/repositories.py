from abc import ABC, abstractmethod
from domain.model import AuthUser, Role, Collaborator, Client, Contract, Event


class AbstractRepository(ABC):
    def __init__(self):
        # implement caching later to reduce redundant DB queries
        self.cached = set()

    def add(self, model_obj):
        self._add(model_obj)

    def get(self, obj_pk):
        return self._get(obj_pk)

    def delete(self, obj_pk):
        self._delete(obj_pk)

    def list(self):
        return self._list()

    def update(self, model_obj):
        self._update(model_obj)

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
    def _update(self, model_obj):
        raise NotImplementedError


class AbstractUserRepository(AbstractRepository):
    @abstractmethod
    def get_by_username(self, username):
        raise NotImplementedError


class AbstractCollaboratorRepository(AbstractRepository):
    @abstractmethod
    def get_by_user_id(self, user_id):
        raise NotImplementedError

    @abstractmethod
    def filter_by_role(self, role):
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

    def _add(self, model_obj):
        self.session.add(model_obj)

    def _get(self, obj_pk):
        return self.session.get(self.model_cls, obj_pk)

    def _delete(self, obj_pk):
        obj = self.session.get(self.model_cls, obj_pk)
        self.session.delete(obj)

    def _list(self):
        return self.session.query(self.model_cls).all()

    def _update(self, model_obj):
        self.session.merge(model_obj)


class SqlAlchemyUserRepository(SqlAlchemyRepository, AbstractUserRepository):
    model_cls = AuthUser

    def get_by_username(self, username):
        return self.session.query(self.model_cls).filter_by(
            username=username).one_or_none()


class SqlAlchemyRoleRepository(SqlAlchemyRepository):
    model_cls = Role


class SqlAlchemyCollaboratorRepository(SqlAlchemyRepository,
                                       AbstractCollaboratorRepository):
    model_cls = Collaborator

    def get_by_user_id(self, user_id):
        return (self.session.query(self.model_cls)
                .filter_by(user_id=user_id).one_or_none())

    def filter_by_role(self, role_id):
        return (self.session.query(self.model_cls)
                .filter_by(role_id=role_id).all())


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
