from abc import ABC


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
                err = self.error_cls(f'{self.model_cls.__name__} not found')
                err.tips = (f"The -pk \"{obj_id}\" isn't linked to an "
                            f"existing {self.model_cls.__name__}. Try a "
                            f"different one.")
                raise err
            return (self.dto_cls.from_domain(obj),)

    def retrieve_all(self, sort=None):
        with self.uow:
            try:
                list_obj = [self.dto_cls.from_domain(obj)
                            for obj in self._repo.list(sort=sort)]
                return tuple(list_obj)
            except AttributeError:
                err = self.error_cls(f'wrong sort key in '
                                     f'{[key for key, _ in sort]}')
                err.tips = ("There was an error in the sorting methods, one of"
                            "the key isn't valid. Verify input and try again")
                raise err

    def remove(self, obj_id):
        with self.uow:
            self._repo.delete(obj_id)
            self.uow.commit()

    def modify(self, obj_id, **kwargs):
        with self.uow:
            obj = self._repo.get(obj_id)
            if obj is None:
                err = self.error_cls(f'{self.model_cls.__name__} not found')
                err.tips = (f"The -pk \"{obj_id}\" isn't linked to an "
                            f"existing {self.model_cls.__name__}. Try a "
                            f"different one.")
                raise err
            for k, v in kwargs.items():
                if v is not None and k in self.model_cls.updatable_fields():
                    setattr(obj, k, v)
            self.uow.commit()

    def filter(self, sort=None, **kwargs):
        filters = {k: v for k, v in kwargs.items()
                   if k in self.model_cls.filterable_fields()}
        if filters == {}:
            err = self.error_cls(f'No valid filters for '
                                 f'{self.model_cls.__name__} in {kwargs}')
            err.tips = ("There was an error in the filtering methods, none of "
                        "the provided filters are valid. "
                        "Verify input and try again")
            raise err
        with self.uow:
            objs = self._repo.filter(sort=sort, **filters)
            return tuple([self.dto_cls.from_domain(obj) for obj in objs])
