"""Abstract service class for basic implementation of CRUD methods.

Classes
    BaseService # Basic implementation of CRUD operation.
"""
from abc import ABC


class BaseService(ABC):
    """Abstract service class for basic implementation of CRUD methods.

    Attributes
        uow (AbstractUnitOfWork): Unit of work exposing repositories.
        model_cls (Any): Domain model class.
        dto_cls (Any): Data Transfer Object class.
        error_cls (Exception): Exception class.
        repo_attr (str): Specific repository attribute name.
    """
    def __init__(self, uow, model_cls, dto_cls, error_cls, repo_attr):
        self.uow = uow
        self.model_cls = model_cls
        self.dto_cls = dto_cls
        self.error_cls = error_cls
        self.repo_attr = repo_attr

    @property
    def _repo(self):
        """Property to get the specific repository name.

        Returns
            Any: Repository instance, as 'self.uow.users' or
                'self.uow.clients' etc.
        """
        return getattr(self.uow, self.repo_attr)

    def create(self, **obj_value):
        """Create and persist a new entity.

        Args
            obj_value (Any): Keywords arguments used to create the
                entity.

        Returns
            Tuple[dto_cls]: Single element tuple containing the DTO of
                the new entity.
        """
        # need to prepare **obj_value in children classes
        with self.uow:
            obj = self.model_cls.builder(**obj_value)
            self._repo.add(obj)
            self.uow.commit()
            return (self.dto_cls.from_domain(obj),)

    def retrieve(self, obj_id):
        """Retrieve an entity by primary key.

        Args
            obj_id (int): Primary key of entity to retrieve.

        Returns
            Tuple[dto_cls]: Single element tuple containing the DTO of
                the entity.

        Raises
            error_cls: if the resource is not found, a class specific
                exception is raised.
        """
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
        """Retrieve all entities of the resource.

        Args
            sort (Iterable(Tuple(str, bool)): An iterable to apply an
                optional sorting to the queries made to the persistence
                layer.

        Returns
            Tuple[dto_cls]: A collection of DTOs of all entities found.

        Raises
            error_cls: if the sort iterable is not properly formated,
                a class specific exception is raised.
        """
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
        """Remove an entity by primary key.

        Args
            obj_id (int): Primary key of entity to delete.
        """
        with self.uow:
            self._repo.delete(obj_id)
            self.uow.commit()

    def modify(self, obj_id, **kwargs):
        """Modify an entity by primary key and persist the change.

        Args
            obj_id (int): Primary key of entity to modify.
            **kwargs (Any): Keyword arguments used to modify the entity.

        Raises
            error_cls: if the object is not found, a class specific
                exception is raised.
        """
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
        """Retrieve entities matching the given criteria.

        Args
            sort (Iterable(Tuple(str, bool)): An iterable to apply an
                optional sorting to the queries made to the persistence
                layer.
            **kwargs (Any): Keyword arguments used to filter entities.

        Returns
            Tuple[dto_cls]: A collection of DTOs of all entities found.

        Raises
            error_cls: if none of the given filters are valid for the
                resource.
        """
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
