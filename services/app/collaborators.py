from domain.model import AuthUser, Collaborator, AuthUserError, Role
from services.dto import CollaboratorDTO
from services.app.base import BaseService, ServiceError


class CollaboratorServiceError(ServiceError):
    pass


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

    def create(self, username, plain_password, role=1, **kwargs):
        with self.uow:
            if self.uow.users.filter_one(username=username):
                raise AuthUserError("username taken")
            AuthUser.builder(username, plain_password)
            user = AuthUser.builder(username, plain_password)
            self.uow.users.add(user)

            obj_value = {k: v for k, v in kwargs.items()
                         if k in self.model_cls.updatable_fields()}
            collaborator = Collaborator.builder(user_id=user.id, role=role,
                                                **obj_value)
            self._repo.add(collaborator)
            self.uow.commit()

    def remove(self, collaborator_id=None):
        with self.uow:
            collaborator = self._repo.get(collaborator_id)
            user = self.uow.users.get(collaborator.user_id)
            self._repo.delete(collaborator_id)
            self.uow.users.delete(user.id)
            self.uow.commit()

    def assign_role(self, collaborator_id, role):
        # need to decide how to handle resources linked to certain roles when
        # user change role (clients of a sales person becoming management ?)
        with self.uow:
            collaborator = self._repo.get(collaborator_id)
            collaborator.role = Role(role)
            self.uow.commit()
