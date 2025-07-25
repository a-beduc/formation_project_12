"""Controller class for the Collaborator resource operations.

Note: when calling for the CollaboratorManager.create method, it will
create a new AuthUser and a new Collaborator at the same time and link
them together.

Classes
    CollaboratorManager # It expands BaseManager to add collaborator
                        # specific operations.
"""
from typing import override

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.auth.predicate import is_management, is_self
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_string
from ee_crm.domain.model import Role
from ee_crm.exceptions import CollaboratorManagerError
from ee_crm.loggers import setup_file_logger, log_sentry_message_event
from ee_crm.services.app.collaborators import CollaboratorService


class CollaboratorManager(BaseManager):
    """Controller for Collaborator resource.

    Inherits from BaseManager, only public attributes differences are
    documented below.

    Attributes
        label: "Collaborator"
        error_cls: CollaboratorManagerError
        service (ee_crm.services.app.collaborators.CollaboratorService):
            The service class to start operations with.
    """
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
    _default_service = CollaboratorService(DEFAULT_UOW())
    error_cls = CollaboratorManagerError

    def _validate_fields(self, fields):
        """See BaseManager._validate_fields

        Differences
            * It add an extra verification for the role field.
        """
        fields_dict = super()._validate_fields(fields)
        if 'role' in fields:
            fields_dict['role'] = self.service.role_sanitizer(fields['role'])
        return fields_dict

    @staticmethod
    def _local_logging_db_action(action, result, resource_id, accountable_id):
        """Local logging setup for logging collaborator resource
        actions.

        Args
            action (str): The performed action. (ex: Update).
            result (str): The result of the action.
                (ex: Updated Collaborator).
            resource_id (int): The id of the resource who was modified.
                (ex: 6).
            accountable_id (int): The id of the collaborator who
                modified the resource. (ex: 6).
        """
        logger = setup_file_logger(name=__name__, filename="ACID")
        logger.info(f'controller ::: Collaborator ::: {action} ::: '
                    f'By collaborator ({accountable_id}) ::: '
                    f'{result} ({resource_id})')

    def _sentry_logging_db_action(self, action, resource_id, accountable_id,
                                  message, level="info", **kwargs):
        """Sentry logging setup for logging collaborator resource
        actions.

        Args
            action (str): The performed action. (ex: Update).
            resource_id (int): The id of the resource who was modified.
                (ex: 6).
            accountable_id (int): The id of the collaborator who
                modified the resource. (ex: 6).
            message (str): The message to log.
                (ex: Updated Collaborator).
            level (str): The level of the log message.
            **kwargs: extra arguments passed to the logger.
        """
        tags = {
            "action": action,
            "resource": self.label.lower(),
            "resource_id": str(resource_id),
            "accountable_id": str(accountable_id)}
        extra = kwargs.get('extra', None)
        user = {"id": accountable_id}
        log_sentry_message_event(message, level,
                                 tags=tags, extra=extra, user=user)

    @override
    @permission("collaborator:create")
    def create(self, username, plain_password, **kwargs):
        """Create a new collaborator and a new user. Override the
        BaseManager.create method.

        Args
            username (str): The username of the user.
            plain_password (str): The password of the user.
            **kwargs: extra arguments passed to create the collaborator.

        Returns
            tuple[dataclass]: A tuple containing an immutable dataclass
                instance exposing the created resource public
                attributes.
        """
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

        self._local_logging_db_action("Create",
                                      "New collaborator",
                                      resource_id,
                                      accountable_id)

        self._sentry_logging_db_action("Create",
                                       resource_id,
                                       accountable_id,
                                       "Collaborator created",
                                       extra={"username": username})

        return collaborator_dto

    @override
    @permission("collaborator:read")
    def read(self, pk=None, filters=None, sort=None):
        """See BaseManager.read"""
        return super().read(pk=pk, filters=filters, sort=sort)

    @override
    @permission("collaborator:update_any", "collaborator:update_self",
                abac=(is_management | is_self))
    def update(self, pk, **kwargs):
        """See BaseManager.update

        Differences
            * limit accepted keyword parameters passed to the service.
        """
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
        self._local_logging_db_action("Update",
                                      "Updated collaborator",
                                      resource_id,
                                      accountable_id)

        self._sentry_logging_db_action("update",
                                       resource_id,
                                       accountable_id,
                                       "Collaborator updated")

    @override
    @permission("collaborator:delete_any", "collaborator:delete_self",
                abac=(is_management | is_self))
    def delete(self, pk, **kwargs):
        """See BaseManager.delete

        Differences
            * Log action
        """
        pk = self._validate_pk_type(pk)
        self.service.remove(collaborator_id=pk, user_id=pk)

        resource_id = pk
        accountable_id = kwargs.get('auth')['c_id']
        self._local_logging_db_action("Delete",
                                      "Removed collaborator",
                                      resource_id,
                                      accountable_id)

        self._sentry_logging_db_action("delete",
                                       resource_id,
                                       accountable_id,
                                       "Collaborator deleted")

    @permission("collaborator:modify_role")
    def change_collaborator_role(self, pk, role, **kwargs):
        """Method that pilot the role attribution of collaborators.

        Args
            pk (int): The primary key/ID of the collaborator.
            role (int|str): The role of the collaborator.
            **kwargs: extra arguments passed to log the user who
                modified the collaborator.
        """
        pk = self._validate_pk_type(pk)
        role = self.service.role_sanitizer(role, strict=True)
        self.service.assign_role(pk, role)

        resource_id = pk
        accountable_id = kwargs.get('auth')['c_id']

        self._local_logging_db_action(
            "Change Role",
            f'Role "{Role(role).name}" for collaborator',
            resource_id,
            accountable_id)

        self._sentry_logging_db_action("change_role",
                                       resource_id,
                                       accountable_id,
                                       f"Collaborator's Role changed to "
                                       f"{Role(role).name}")
