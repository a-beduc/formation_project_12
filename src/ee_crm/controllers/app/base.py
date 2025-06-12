from abc import ABC
from ee_crm.services.unit_of_work import AbstractUnitOfWork


class BaseManager(ABC):
    label: str
    _validate_types: dict
    _default_service: AbstractUnitOfWork

    def __init__(self, service=None):
        self.service = service or self._default_service

    def _validate_fields(self, fields):
        return {
            k: self._validate_types[k](v)
            for k, v in fields.items() if k in self._validate_types
        }

    def create(self, **kwargs):
        data = self._validate_fields(kwargs)
        self.service.create(**data)

    def read(self, pk=None, filters=None, sort=None):
        if pk:
            return self.service.retrieve(int(pk))

        if filters:
            validated_filters = self._validate_fields(filters)
            output_dto = self.service.filter(sort=sort, **validated_filters)
        else:
            output_dto = self.service.retrieve_all(sort=sort)

        return output_dto

    def update(self, pk, **kwargs):
        data = self._validate_fields(kwargs)
        self.service.modify(obj_id=int(pk), **data)

    def delete(self, pk):
        self.service.remove(int(pk))
