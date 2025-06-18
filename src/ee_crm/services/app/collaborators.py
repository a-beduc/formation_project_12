from ee_crm.domain.model import AuthUser, Collaborator, Role
from ee_crm.exceptions import CollaboratorServiceError, CollaboratorDomainError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import CollaboratorDTO


class CollaboratorService(BaseService):
    # need to sanitize user input at controller layer
    def __init__(self, uow):
        super().__init__(
            uow,
            Collaborator,
            CollaboratorDTO,
            CollaboratorServiceError,
            "collaborators"
        )

    @staticmethod
    def role_sanitizer(role, strict=False):
        if strict:
            return Role.sanitizer(role)
        try:
            return Role.sanitizer(role)
        except CollaboratorDomainError:
            # used to filter out every role for queries with invalid Role input
            return -1

    def create(self, username, plain_password, role=1, **kwargs):
        with self.uow:
            if self.uow.users.filter_one(username=username):
                raise self.error_cls("username taken")
            AuthUser.builder(username, plain_password)
            user = AuthUser.builder(username, plain_password)
            self.uow.users.add(user)

            obj_value = {k: v for k, v in kwargs.items()
                         if k in self.model_cls.updatable_fields()}

            self.uow.session.flush()
            collaborator = Collaborator.builder(user_id=user.id, role=role,
                                                **obj_value)
            self._repo.add(collaborator)
            self.uow.commit()

    def remove(self, collaborator_id=None, user_id=None):
        with self.uow:
            if collaborator_id:
                collaborator = self._repo.get(collaborator_id)
                user = self.uow.users.get(collaborator.user_id)
            elif user_id:
                user = self.uow.users.get(user_id)
                collaborator = self._repo.filter(user_id=user.id)
            self._repo.delete(collaborator.id)
            self.uow.users.delete(user.id)
            self.uow.commit()

    def assign_role(self, collaborator_id, role):
        # need to decide how to handle resources linked to certain roles when
        # user change role (clients of a sales person becoming management ?)
        with self.uow:
            roles = {
                Role.DEACTIVATED,
                Role.MANAGEMENT,
                Role.SALES,
                Role.SUPPORT
            }
            if role not in roles:
                raise CollaboratorServiceError(f"Invalid role: {role}")
            collaborator = self._repo.get(collaborator_id)
            collaborator.role = role
            self.uow.commit()
