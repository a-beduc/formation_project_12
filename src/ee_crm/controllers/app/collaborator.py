from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork
from ee_crm.services.app.collaborators import CollaboratorService

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.permission import permission, is_management, is_self
from ee_crm.domain.model import Role


class CollaboratorManager(BaseManager):
    label = "Collaborator"
    _validate_types = {
        "id": int,
        "last_name": str,
        "first_name": str,
        "email": str,
        "phone_number": str,
        "role": str,
        "user_id": int
    }
    _default_service = CollaboratorService(SqlAlchemyUnitOfWork())

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
    def update(self, pk, update_data, **kwargs):
        update_fields = {
            "last_name",
            "first_name",
            "email",
            "phone_number"
        }
        update_data = {k: v for k, v in kwargs.items() if k in update_fields}
        validated_data = self._validate_fields(update_data)
        return super().update(pk=pk, **validated_data)

    @permission(requirements=(is_management | is_self))
    def delete(self, pk, **kwargs):
        validated_pk = int(pk)
        self.service.remove(collaborator_id=validated_pk, user_id=validated_pk)

    @permission(requirements=is_management)
    def change_collaborator_role(self, pk, role):
        collaborator_id = int(pk)
        role = Role.sanitizer(role)
        self.service.assign_role(collaborator_id, role)
