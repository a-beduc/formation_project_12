from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.permission import permission, is_management, is_self
from ee_crm.controllers.utils import verify_positive_int, verify_string
from ee_crm.exceptions import CollaboratorManagerError
from ee_crm.services.app.collaborators import CollaboratorService
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork


class CollaboratorManager(BaseManager):
    label = "Collaborator"
    _validate_types_map = {
        "id": verify_positive_int,
        "last_name": verify_string,
        "first_name": verify_string,
        "email": verify_string,
        "phone_number": verify_string,
        "role": verify_string,
        "user_id": verify_positive_int
    }
    _default_service = CollaboratorService(SqlAlchemyUnitOfWork())
    error_cls = CollaboratorManagerError

    def _validate_fields(self, fields):
        fields_dict = super()._validate_fields(fields)
        if 'role' in fields:
            try:
                fields_dict['role'] = Role.sanitizer(fields['role'])
            except CollaboratorError:
                pass
        return fields_dict

    @permission(requirements=is_management)
    def create(self, username, plain_password, **kwargs):
        create_fields = {
            "last_name",
            "first_name",
            "email",
            "phone_number",
            "role"
        }
        role = kwargs.pop('role', "DEACTIVATED")
        role = Role.sanitizer(role)
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        validated_data = self._validate_fields(create_data)
        self.service.create(username, plain_password, role=role,
                            **validated_data)

    @permission
    def read(self, pk=None, filters=None, sort=None):
        return super().read(pk=pk, filters=filters, sort=sort)

    @permission(requirements=(is_management | is_self))
    def update(self, pk, **kwargs):
        update_fields = {
            "last_name",
            "first_name",
            "email",
            "phone_number"
        }
        update_data = {k: v for k, v in kwargs.items() if k in
                       update_fields}
        return super().update(pk=pk, **update_data)

    @permission(requirements=(is_management | is_self))
    def delete(self, pk, **kwargs):
        pk = self._validate_pk_type(pk)
        self.service.remove(collaborator_id=pk, user_id=pk)

    @permission(requirements=is_management)
    def change_collaborator_role(self, pk, role):
        pk = self._validate_pk_type(pk)
        role = Role.sanitizer(role)
        self.service.assign_role(pk, role)
