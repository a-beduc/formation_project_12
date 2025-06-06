from abc import ABC


class ServiceError(Exception):
    pass


class BaseService(ABC):
    def __init__(self, uow, model_cls, dto_cls, error_cls, repo_attr):
        self.uow = uow
        self.model_cls = model_cls
        self.dto_cls = dto_cls
        self.error_cls = error_cls
        self.repo_attr = repo_attr

    @property
    def _repo(self):
        return getattr(self.uow, self.repo_attr)

    def create(self, **obj_value):
        # need to prepare **obj_value in children classes
        obj = self.model_cls.builder(**obj_value)
        with self.uow:
            self._repo.add(obj)
            self.uow.commit()

    def retrieve(self, obj_id):
        with self.uow:
            obj = self._repo.get(obj_id)
            if obj is None:
                raise self.error_cls(f'{self.model_cls.__name__} not found')
            return self.dto_cls.from_domain(obj)

    def retrieve_all(self):
        with self.uow:
            return [self.dto_cls.from_domain(obj) for obj in self._repo.list()]

    def remove(self, obj_id):
        with self.uow:
            self._repo.delete(obj_id)
            self.uow.commit()

    def modify(self, obj_id, **kwargs):
        with self.uow:
            obj = self._repo.get(obj_id)
            if obj is None:
                raise self.error_cls(f'{self.model_cls.__name__} not found')
            for k, v in kwargs.items():
                if v is not None and k in self.model_cls.updatable_fields():
                    setattr(obj, k, v)
            self.uow.commit()

    def filter(self, **kwargs):
        filters = {k: v for k, v in kwargs.items()
                   if k in self.model_cls.filterable_fields()}
        if filters == {}:
            raise self.error_cls(f'No valid filters for '
                                 f'{self.model_cls.__name__} in {kwargs}')
        with self.uow:
            objs = self._repo.filter(**filters)
            return [self.dto_cls.from_domain(obj) for obj in objs]

    def sort(self, *dto_objects, key, reverse=False):
        if key not in self.model_cls.filterable_fields():
            raise self.error_cls(f'Unknown sort key: {key}')
        return sorted(dto_objects, key=lambda d: getattr(d, key),
                      reverse=reverse)
