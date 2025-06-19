from abc import ABC

from ee_crm.controllers.utils import InputError, verify_positive_int
from ee_crm.exceptions import BaseManagerError
from ee_crm.services.unit_of_work import AbstractUnitOfWork


class BaseManager(ABC):
    label: str
    _validate_types_map: dict
    _default_service: AbstractUnitOfWork
    error_cls: BaseManagerError = BaseManagerError

    def __init__(self, service=None):
        self.service = service or self._default_service

    def _validate_pk_type(self, pk):
        try:
            return verify_positive_int(pk)
        except InputError as e:
            err = self.error_cls(f"{e.args[0]}. Input <-pk: {pk}>.")
            err.threat = e.threat
            err.tips = (f"{e.tips} Verify your input <pk: {pk}> in the "
                        f"command and try again.")
            raise err

    def _validate_types(self, key, value):
        try:
            return self._validate_types_map[key](value)
        except InputError as e:
            err = self.error_cls(f"{e.args[0]}")
            err.threat = e.threat
            err.tips = (f"{e.tips} Verify your input <{key}: {value}> in the "
                        f"command and try again.")
            raise err

    def _validate_fields(self, fields):
        return {
            k: self._validate_types(k, v)
            for k, v in fields.items() if k in self._validate_types_map
        }

    def create(self, **kwargs):
        data = self._validate_fields(kwargs)
        self.service.create(**data)

    def read(self, pk=None, filters=None, sort=None):
        if pk:
            pk = self._validate_pk_type(pk)
            return self.service.retrieve(pk)

        if filters:
            validated_filters = self._validate_fields(filters)
            output_dto = self.service.filter(sort=sort, **validated_filters)
        else:
            output_dto = self.service.retrieve_all(sort=sort)

        return output_dto

    def update(self, pk, **kwargs):
        pk = self._validate_pk_type(pk)
        data = self._validate_fields(kwargs)
        self.service.modify(obj_id=pk, **data)

    def delete(self, pk):
        pk = self._validate_pk_type(pk)
        self.service.remove(pk)
