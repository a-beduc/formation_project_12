from abc import ABC, abstractmethod


class AbstractRepository(ABC):
    def __init__(self):
        # implement caching later to reduce redundant DB queries
        self.cached = set()

    def add(self, model_obj):
        self._add(model_obj)

    def get(self, model_cls, obj_pk):
        return self._get(model_cls, obj_pk)

    def delete(self, model_cls, obj_pk):
        self._delete(model_cls, obj_pk)

    def list(self, model_cls):
        return self._list(model_cls)

    def update(self, model_obj):
        self._update(model_obj)

    @abstractmethod
    def _add(self, model_obj):
        raise NotImplementedError

    @abstractmethod
    def _get(self, model_cls, obj_pk):
        raise NotImplementedError

    @abstractmethod
    def _delete(self, model_cls, obj_pk):
        raise NotImplementedError

    @abstractmethod
    def _list(self, model_cls):
        raise NotImplementedError

    @abstractmethod
    def _update(self, model_obj):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, model_obj):
        self.session.add(model_obj)

    def _get(self, model_cls, obj_pk):
        return self.session.get(model_cls, obj_pk)

    def _delete(self, model_cls, obj_pk):
        obj = self.session.get(model_cls, obj_pk)
        self.session.delete(obj)

    def _list(self, model_cls):
        return self.session.query(model_cls).all()

    def _update(self, model_obj):
        self.session.merge(model_obj)
