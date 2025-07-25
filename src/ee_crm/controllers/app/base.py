"""Controller class for basic implementation of CRUD operations and
input validation.

Classes
    BaseManager # Basic implementation of CRUD operations.
"""
from ee_crm.controllers.utils import InputError, verify_positive_int
from ee_crm.exceptions import BaseManagerError
from ee_crm.services.app.base import BaseService


class BaseManager:
    """Base controller class for basic implementation of CRUD
    operations and input validation.

    Attributes
        label (str): (class attribute) Name of the resource.
        _validate_types_map (dict): (class attribute) mapping between
            resource attribute (key) and validation helper (value).
        _default_service (ee_crm.services.app.base.BaseService):
            (class attribute) Resource specific service class.
        error_cls (BaseManagerError): (class attribute) Exception class raised
            when an error occurs.

        service (ee_crm.services.app.base.BaseService): The service
            class to start operations with.
    """
    label: str
    _validate_types_map: dict
    _default_service: BaseService
    error_cls: BaseManagerError = BaseManagerError

    def __init__(self, service=None):
        self.service = service or self._default_service

    def _validate_pk_type(self, pk):
        """Helper method to verify that given pk is a positive integer.

        Args
            pk (int): The primary key.

        Raises
            BaseManagerError: If pk is not a positive integer.
        """
        try:
            return verify_positive_int(pk)
        except InputError as e:
            err = self.error_cls(f"{e.args[0]}. Input <-pk: {pk}>.")
            err.threat = e.threat
            err.tips = (f"{e.tips} Verify your input <pk: {pk}> in the "
                        f"command and try again.")
            raise err

    def _validate_types(self, key, value):
        """Helper method to verify that given value is of a valid type.

        Args
            key (str): The name of the attribute.
            value (Any): The value to validate.

        Returns
            Any: The value converted to the expected type.

        Raises
            BaseManagerError: If value can't be converted to the valid
                type.
        """
        try:
            return self._validate_types_map[key](value)
        except InputError as e:
            err = self.error_cls(f"{e.args[0]}")
            err.threat = e.threat
            err.tips = (f"{e.tips} Verify your input <{key}: {value}> in the "
                        f"command and try again.")
            raise err

    def _validate_fields(self, fields):
        """Helper method to verify that given fields are valid.
        It ignores the key-value pairs where the key is not part of the
        expected keys.

        Args
            fields (dict): The fields to validate.

        Returns
            dict: The validated fields. Some value may be converted to
                the expected type.
        """
        return {
            k: self._validate_types(k, v)
            for k, v in fields.items() if k in self._validate_types_map
        }

    def create(self, **kwargs):
        """Start the create operation. It creates and persist a new
        resource.

        Args
            **kwargs (dict): Keyword arguments that may be passed to
                the creation service.

        Returns
            tuple[dataclass]: A tuple containing an immutable dataclass
                instance exposing the created resource public
                attributes.
        """
        data = self._validate_fields(kwargs)
        obj_dto = self.service.create(**data)
        return obj_dto

    def read(self, pk=None, filters=None, sort=None):
        """Start the read operation. It reads and returns a tuple
        containing the result of the query.

        Args
            pk (int): The primary key.
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.

        Returns
            tuple[dataclass]: A tuple containing the result of the
                query.
        """
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
        """Start the update operation. It updates an existing resource
        and persist the modification.

        Args
            pk (int): The primary key of the resource.
            **kwargs (dict): Keyword arguments that may be passed to the
                update service.
        """
        pk = self._validate_pk_type(pk)
        data = self._validate_fields(kwargs)
        self.service.modify(obj_id=pk, **data)

    def delete(self, pk):
        """Start the delete operation. It deletes an existing resource
        from the persistence layer.

        Args
            pk (int): The primary key of the resource.
        """
        pk = self._validate_pk_type(pk)
        self.service.remove(pk)
