from abc import ABC, abstractmethod
import domain.model as model


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, model_obj):
        raise NotImplementedError

    @abstractmethod
    def get(self, obj_id):
        raise NotImplementedError

    @abstractmethod
    def delete(self, model_obj):
        raise NotImplementedError

    @abstractmethod
    def list(self):
        raise NotImplementedError

    @abstractmethod
    def update(self, model_obj):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, model_obj):
        self.session.add(model_obj)

    def get(self, obj_id):
        return self.session.query(model.AuthUser).filter_by(id=obj_id).one()

    def delete(self, model_obj):
        obj = self.session.merge(model_obj)
        self.session.delete(obj)

    def list(self):
        return self.session.query(model.AuthUser).all()

    def update(self, model_obj):
        self.session.merge(model_obj)
