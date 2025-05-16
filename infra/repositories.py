from abc import ABC, abstractmethod
import domain.model as model


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, auth_user):
        raise NotImplementedError

    @abstractmethod
    def get(self, user_id):
        raise NotImplementedError

    @abstractmethod
    def delete(self, auth_user):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, auth_user):
        self.session.add(auth_user)

    def get(self, user_id):
        return self.session.query(model.AuthUser).filter_by(id=user_id).one()

    def delete(self, auth_user):
        obj = self.session.merge(auth_user)
        self.session.delete(obj)

    def list(self):
        return self.session.query(model.AuthUser).all()

    def update(self, auth_user):
        self.session.merge(auth_user)
