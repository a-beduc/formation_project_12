from abc import ABC, abstractmethod

from ee_crm.domain.model import AuthUser, Collaborator, Client, Contract, Event


class AbstractRepository(ABC):

    def add(self, model_obj):
        self._add(model_obj)

    def get(self, obj_pk):
        return self._get(obj_pk)

    def delete(self, obj_pk):
        self._delete(obj_pk)

    def list(self, sort=None):
        return self._list(sort=sort)

    def filter(self, sort=None, **filters):
        return self._filter(sort=sort, **filters)

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
    def _list(self, sort=None):
        raise NotImplementedError

    @abstractmethod
    def _filter(self, sort=None, **filters):
        raise NotImplementedError

    @abstractmethod
    def _filter_one(self, **filters):
        raise NotImplementedError


class ContractAbstractRepository(ABC):
    @abstractmethod
    def get_contracts_collaborator(self,
                                   collaborator_id,
                                   only_unpaid=False,
                                   only_unsigned=False,
                                   only_no_event=False,
                                   sort=None, **filters):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    model_cls = None

    def __init__(self, session):
        super().__init__()
        self.session = session

    def _translate_filters(self, filters):
        aliases = getattr(self.model_cls, "_private_aliases", {})
        return {aliases.get(k, k): v for k, v in filters.items()}

    def _translate_sort(self, sort):
        # sort must be a tuple/list
        aliases = getattr(self.model_cls, "_private_aliases", {})
        ordering = [(aliases.get(e[0], e[0]), e[1]) for e in sort]

        order_output = []
        for field, is_desc in ordering:
            attr = getattr(self.model_cls, field)
            if is_desc is True:
                order_output.append(attr.desc())
            else:
                order_output.append(attr.asc())
        return tuple(order_output)

    def _add(self, model_obj):
        self.session.add(model_obj)

    def _get(self, obj_pk):
        return self.session.get(self.model_cls, obj_pk)

    def _delete(self, obj_pk):
        obj = self.session.get(self.model_cls, obj_pk)
        self.session.delete(obj)

    def _list(self, sort=None):
        query = self.session.query(self.model_cls)
        if sort is not None:
            order = self._translate_sort(sort)
            query = query.order_by(*order)
        return query.all()

    def _filter(self, sort=None, **filters):
        orm_filters = self._translate_filters(filters)
        query = self.session.query(self.model_cls).filter_by(**orm_filters)
        if sort is not None:
            order = self._translate_sort(sort)
            query = query.order_by(*order)
        return query.all()

    def _filter_one(self, **filters):
        orm_filters = self._translate_filters(filters)
        query = self.session.query(self.model_cls).filter_by(**orm_filters)
        return query.one_or_none()


class SqlAlchemyUserRepository(SqlAlchemyRepository):
    model_cls = AuthUser


class SqlAlchemyCollaboratorRepository(SqlAlchemyRepository):
    model_cls = Collaborator


class SqlAlchemyClientRepository(SqlAlchemyRepository):
    model_cls = Client


class SqlAlchemyContractRepository(SqlAlchemyRepository,
                                   ContractAbstractRepository):
    model_cls = Contract

    def get_contracts_collaborator(self,
                                   collaborator_id,
                                   only_unpaid=False,
                                   only_unsigned=False,
                                   only_no_event=False,
                                   sort=None, **filters):
        orm_filters = self._translate_filters(filters)

        query = (self.session.query(self.model_cls)
                 .filter_by(**orm_filters)
                 .join(Client)
                 .filter(Client.salesman_id_sql == collaborator_id))

        if only_unpaid is True:
            query = query.filter((self.model_cls.due_amount_sql > 0))

        if only_unsigned is True:
            # self.model_cls.signed is False doesn't work for some reason
            query = query.filter((self.model_cls.signed_sql == False))

        if only_no_event is True:
            # self.model_cls.event is None doesn't work for some reason
            query = query.filter((self.model_cls.event == None))

        if sort is not None:
            order = self._translate_sort(sort)
            query = query.order_by(*order)
        return query.all()


class SqlAlchemyEventRepository(SqlAlchemyRepository):
    model_cls = Event
