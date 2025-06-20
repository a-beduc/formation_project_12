from ee_crm.config import setup_file_logger
from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.permission import permission, is_management, is_self
from ee_crm.controllers.utils import verify_positive_int, verify_string
from ee_crm.domain.model import Role
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
            fields_dict['role'] = self.service.role_sanitizer(fields['role'])
        return fields_dict

    @staticmethod
    def _logging_acid_action(action, result, resource_id, accountable_id):
        logger = setup_file_logger(name=__name__, filename="ACID")
        logger.info(f'controller ::: Collaborator ::: {action} ::: '
                    f'by collaborator ({accountable_id}) ::: '
                    f'{result} ({resource_id})')

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
        role = self.service.role_sanitizer(role, strict=True)
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        validated_data = self._validate_fields(create_data)

        collaborator_dto = self.service.create(username, plain_password,
                                               role=role, **validated_data)

        resource_id = collaborator_dto[0].id
        accountable_id = kwargs.get('auth')['c_id']
        self._logging_acid_action("Create",
                                  "New collaborator",
                                  resource_id,
                                  accountable_id)

        return collaborator_dto

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
        super().update(pk=pk, **update_data)

        resource_id = pk
        accountable_id = kwargs.get('auth')['c_id']
        self._logging_acid_action("Update",
                                  "Updated collaborator",
                                  resource_id,
                                  accountable_id)

    @permission(requirements=(is_management | is_self))
    def delete(self, pk, **kwargs):
        pk = self._validate_pk_type(pk)
        self.service.remove(collaborator_id=pk, user_id=pk)

        resource_id = pk
        accountable_id = kwargs.get('auth')['c_id']
        self._logging_acid_action("Delete",
                                  "Removed collaborator",
                                  resource_id,
                                  accountable_id)

    @permission(requirements=is_management)
    def change_collaborator_role(self, pk, role, **kwargs):
        pk = self._validate_pk_type(pk)
        role = self.service.role_sanitizer(role, strict=True)
        self.service.assign_role(pk, role)

        resource_id = pk
        accountable_id = kwargs.get('auth')['c_id']
        self._logging_acid_action(
            "Change Role",
            f'Role "{Role(role).name}" for collaborator',
            resource_id,
            accountable_id)
