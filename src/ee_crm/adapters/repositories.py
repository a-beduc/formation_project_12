"""Repository pattern interface between Domain and DAL (Data Access Layer).

Classes
    AbstractRepository                  # Abstraction of Repositories
    ContractAbstractRepository          # Add specific method for Contracts
    SqlAlchemyRepository                # SQLAlchemy shared implementation
    SqlAlchemyUserRepository            # SQLAlchemy implementation
    SqlAlchemyCollaboratorRepository    # SQLAlchemy implementation
    SqlAlchemyClientRepository          # SQLAlchemy implementation
    SqlAlchemyContractRepository        # SQLAlchemy implementation
    SqlAlchemyEventRepository           # SQLAlchemy implementation

References
    * Architecture Patterns with Python.
https://www.cosmicpython.com/book/chapter_02_repository.html
"""
from abc import ABC, abstractmethod

from ee_crm.domain.model import AuthUser, Collaborator, Client, Contract, Event


class AbstractRepository(ABC):
    """Generic CRUD methods used by the service layer. Public methods
    must be implemented through private methods in subclasses.

    Public methods:
        add(model_obj)
        get(obj_pk)
        delete(obj_pk)
        list(sort=None)
        filter(sort=None, **filters)
        filter_one(**filters)
    """
    def add(self, model_obj):
        """Add a new object.
        Delegate implementation to private method.

        Args:
            model_obj (Any): Object to be added.
        """
        self._add(model_obj)

    def get(self, obj_pk):
        """Fetch an object by pk.
        Delegate implementation to private method.

        Args:
            obj_pk (int): Primary key of object to be fetched.

        Returns:
            (None|Any): None or object retrieved.
        """
        return self._get(obj_pk)

    def delete(self, obj_pk):
        """Delete an object by pk.
        Delegate implementation to private method.

        Args:
            obj_pk (int): Primary key of object to be deleted.
        """
        self._delete(obj_pk)

    def list(self, sort=None):
        """Fetch list of all objects.
        Delegate implementation to private method.

        Args:
            sort (Iterable[tuple(str, bool)]|None): Optional sorting
                criteria.

        Returns:
            (Iterable[Any]|None): None or list of objects retrieved.
        """
        return self._list(sort=sort)

    def filter(self, sort=None, **filters):
        """Filter objects based on filters.
        Delegate implementation to private method.

        Args:
            sort (Iterable[tuple(str, bool)]|None): Optional sorting
                criteria.
            **filters (dict): Optional filter criteria.

        Returns:
            (Iterable[Any]|None): None or list of objects retrieved.
        """
        return self._filter(sort=sort, **filters)

    def filter_one(self, **filters):
        """Filter one object based on filters.
        Delegate implementation to private method.

        Args:
            **filters (dict): Optional filter criteria.

        Returns:
            (Any|None): None or object retrieved.
        """
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
    def _list(self, sort=None):
        raise NotImplementedError

    @abstractmethod
    def _filter(self, sort=None, **filters):
        raise NotImplementedError

    @abstractmethod
    def _filter_one(self, **filters):
        raise NotImplementedError


class ContractAbstractRepository(ABC):
    """Extension of AbstractRepository to provide specific additional
    methods."""
    @abstractmethod
    def get_contracts_collaborator(self,
                                   collaborator_id,
                                   only_unpaid=False,
                                   only_unsigned=False,
                                   only_no_event=False,
                                   sort=None, **filters):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    """Reusable SQLAlchemy implementation of the repository interface.

    Attributes:
        model_cls (Class): Domain model class added in subclasses.
        session: SQLAlchemy session object. (Already mapped).
    """
    model_cls = None

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _translate_filters(self, filters):
        """Helper used to map public fields name to private attributes.

        It uses the model_cls._private_aliases attribute to change key
        found in input dict. (ex: {"role_id": 5} -> {"_role_id": 5}).

        Args:
            filters (dict): filter criteria.

        Returns:
            (dict): remapped dict.
        """
        aliases = getattr(self.model_cls, "_private_aliases", {})
        return {aliases.get(k, k): v for k, v in filters.items()}

    def _translate_sort(self, sort):
        """Helper used create a tuple of SQLAlchemy Unary expressions.

        It uses the model_cls._private_aliases attribute to change first
        value found in tuples representing sort.
        (ex: [("role_id", True)] -> [crm.collaborator.role_id DESC])

        Args:
            sort (Iterable[tuple(str, bool)]|None): Optional sorting
                criteria.

        Returns:
            (tuple[UnaryExpression|None]): tuple of SQLAlchemy Unary
                expressions.

        References:
            * https://docs.sqlalchemy.org/en/21/core/sqlelement.html#sqlalchemy.sql.expression.UnaryExpression
            * https://docs.sqlalchemy.org/en/21/core/sqlelement.html#sqlalchemy.sql.expression.asc
        """
        aliases = getattr(self.model_cls, "_private_aliases", {})
        ordering = [(aliases.get(e[0], e[0]), e[1]) for e in sort]

        order_output = []
        for field, is_desc in ordering:
            attr = getattr(self.model_cls, field)
            if is_desc is True:
                order_output.append(attr.desc())
            else:
                order_output.append(attr.asc())
        print(order_output[0])
        return tuple(order_output)

    def _add(self, model_obj):
        """Implementation using SQLAlchemy add.
        For signature details, refer to AbsractRepository.add().
        """
        self.session.add(model_obj)

    def _get(self, obj_pk):
        """Implementation using SQLAlchemy get.
        For signature details, refer to AbsractRepository.get().
        """
        return self.session.get(self.model_cls, obj_pk)

    def _delete(self, obj_pk):
        """Implementation using SQLAlchemy delete.
        For signature details, refer to AbsractRepository.delete().
        """
        obj = self.session.get(self.model_cls, obj_pk)
        self.session.delete(obj)

    def _list(self, sort=None):
        """Implementation using SQLAlchemy query.
        For signature details, refer to AbsractRepository.list().
        """
        query = self.session.query(self.model_cls)
        if sort is not None:
            order = self._translate_sort(sort)
            query = query.order_by(*order)
        return query.all()

    def _filter(self, sort=None, **filters):
        """Implementation using SQLAlchemy query.
        For signature details, refer to AbsractRepository.filter().
        """
        orm_filters = self._translate_filters(filters)
        query = self.session.query(self.model_cls).filter_by(**orm_filters)
        if sort is not None:
            order = self._translate_sort(sort)
            query = query.order_by(*order)
        return query.all()

    def _filter_one(self, **filters):
        """Implementation using SQLAlchemy query.
        For signature details, refer to AbsractRepository.filter_one().
        """
        orm_filters = self._translate_filters(filters)
        query = self.session.query(self.model_cls).filter_by(**orm_filters)
        return query.one_or_none()


class SqlAlchemyUserRepository(SqlAlchemyRepository):
    """SQLAlchemy user repository implementation."""
    model_cls = AuthUser


class SqlAlchemyCollaboratorRepository(SqlAlchemyRepository):
    """SQLAlchemy collaborator repository implementation."""
    model_cls = Collaborator


class SqlAlchemyClientRepository(SqlAlchemyRepository):
    """SQLAlchemy client repository implementation."""
    model_cls = Client


class SqlAlchemyContractRepository(SqlAlchemyRepository,
                                   ContractAbstractRepository):
    """SQLAlchemy contract repository implementation."""
    model_cls = Contract

    def get_contracts_collaborator(self,
                                   collaborator_id,
                                   only_unpaid=False,
                                   only_unsigned=False,
                                   only_no_event=False,
                                   sort=None, **filters):
        """SQLAlchemy Implementation of method specific to contracts.
        Return contracts belonging to a salesman.

        It leverages synonym and column_property to make the queries,
        see ee_crm.adapters.orm.py docstrings for more information.

        Args:
            collaborator_id (int): Primary key of collaborator
            only_unpaid (bool): If True, only unpaid collaborators are
                returned.
            only_unsigned (bool): If True, only unsigned collaborators
                are returned.
            only_no_event (bool): If True, only contracts who have no
                linked events are returned.
            sort (Iterable[tuple(str, bool)]|None): Optional sorting
                criteria.
            **filters (dict): Optional filter criteria.

        Returns:
            (list(Contract|None)): List of contracts.
        """
        orm_filters = self._translate_filters(filters)

        query = (self.session.query(self.model_cls)
                 .filter_by(**orm_filters)
                 .join(Client)
                 .filter(Client.salesman_id_sql == collaborator_id))

        if only_unpaid:
            query = query.filter((self.model_cls.due_amount_sql > 0))

        if only_unsigned is True:
            # self.model_cls.signed is False doesn't work for some reason.
            query = query.filter((self.model_cls.signed_sql == False))

        if only_no_event is True:
            # self.model_cls.event is None doesn't work for some reason.
            query = query.filter((self.model_cls.event == None))

        if sort is not None:
            order = self._translate_sort(sort)
            query = query.order_by(*order)
        return query.all()


class SqlAlchemyEventRepository(SqlAlchemyRepository):
    """SQLAlchemy event repository implementation."""
    model_cls = Event
