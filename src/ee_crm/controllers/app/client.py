from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.permission import permission, is_sales, \
    is_client_associated_salesman
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_string, \
    verify_datetime
from ee_crm.exceptions import ClientManagerError
from ee_crm.services.app.clients import ClientService


class ClientManager(BaseManager):
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

    @permission(requirements=is_sales)
    def create(self, **kwargs):
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

    @permission
    def read(self, pk=None, filters=None, sort=None):
        return super().read(pk=pk, filters=filters, sort=sort)

    @permission(requirements=is_client_associated_salesman)
    def update(self, pk, **kwargs):
        update_fields = {
            "last_name",
            "first_name",
            "email",
            "phone_number",
            "company"
        }
        update_data = {k: v for k, v in kwargs.items() if k in update_fields}
        return super().update(pk=pk, **update_data)

    @permission(requirements=is_client_associated_salesman)
    def delete(self, pk, **kwargs):
        return super().delete(pk=pk)
