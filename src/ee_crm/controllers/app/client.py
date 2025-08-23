"""Controller class for the Client resource operations.

Classes
    ClientManager   # It expands BaseManager to add client specific
                    # operations.
"""
from typing import override

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.auth.predicate import is_client_associated_salesman, \
    is_management, client_has_salesman
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_string, \
    verify_datetime
from ee_crm.exceptions import ClientManagerError
from ee_crm.services.app.clients import ClientService


class ClientManager(BaseManager):
    """Controller for Client resource.

    Inherits from BaseManager, only public attributes differences are
    documented below.

    Attributes
        label: "Client"
        error_cls: ClientManagerError
        service (ee_crm.services.app.clients.ClientService): The service
            class to start operations with.
    """
    label = "Client"
    _validate_types_map = {
        "id": verify_positive_int,
        "last_name": verify_string,
        "first_name": verify_string,
        "email": verify_string,
        "phone_number": verify_string,
        "company": verify_string,
        "created_at": verify_datetime,
        "updated_at": verify_datetime,
        "salesman_id": verify_positive_int
    }
    _default_service = ClientService(DEFAULT_UOW())
    error_cls = ClientManagerError

    @override
    @permission("client:create")
    def create(self, **kwargs):
        """See BaseManager.create

        Differences
            * limit accepted keyword parameters passed to the service.
            * inject salesman_id from kwargs["auth"]["c_id"].
        """
        create_fields = {
            "last_name",
            "first_name",
            "email",
            "phone_number",
            "company"
        }
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        create_data["salesman_id"] = kwargs["auth"]["c_id"]
        return super().create(**create_data)

    @override
    @permission("client:read")
    def read(self, pk=None, filters=None, sort=None):
        """See BaseManager.read"""
        return super().read(pk=pk, filters=filters, sort=sort)

    @override
    @permission("client:update_own", "client:update_unassigned",
                abac=(is_client_associated_salesman |
                      (is_management & ~client_has_salesman)))
    def update(self, pk, **kwargs):
        """See BaseManager.update

        Differences
            * limit accepted keyword parameters passed to the service.
        """
        update_fields = {
            "last_name",
            "first_name",
            "email",
            "phone_number",
            "company"
        }
        update_data = {k: v for k, v in kwargs.items() if k in update_fields}
        return super().update(pk=pk, **update_data)

    @override
    @permission("client:delete_own", "client:delete_unassigned",
                abac=(is_client_associated_salesman |
                      (is_management & ~client_has_salesman)))
    def delete(self, pk, **kwargs):
        """See BaseManager.delete"""
        return super().delete(pk=pk)

    @permission("client:read")
    def user_associated_resource(self, filters, sort, **kwargs):
        """Method that pilot the operation to retrieve the clients
        for which the salesman is the user.

        Args
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.
            **kwargs (dict): Keyword arguments to pass the context.

        Returns
            tuple[dataclass]: A tuple containing the result of the
                query.
        """
        if filters is None:
            filters = {}
        filters['salesman_id'] = kwargs['auth']['c_id']
        return super().read(pk=None, filters=filters, sort=sort)

    @permission("client:read")
    def orphan_clients(self, filters, sort):
        """Method that pilot the operation to retrieve the clients that
        are lacking a salesman.

        Args
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.

        Returns
            tuple[dataclass]: A tuple containing the result of the
                query.
        """
        if filters is None:
            filters = {}
        validated_filters = self._validate_fields(filters)
        validated_filters['salesman_id'] = None
        output_dto = self.service.filter(sort=sort, **validated_filters)
        return output_dto
