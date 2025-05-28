from domain.model import AuthUser, Collaborator, AuthUserError
from services.dto import CollaboratorDTO, AuthUserDTO
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

    def create(self, username, plain_password, **kwargs):
        AuthUser.validate_password(plain_password)
        AuthUser.validate_username(username)
        user = AuthUser.build_user(username, plain_password)

        if kwargs.get("role_id", None) is None:
            kwargs["role_id"] = 1
        obj_value = {k: kwargs.get(k, None) for k in self.updatable_fields}

        collaborator = Collaborator(user_id=None, **obj_value)

        with self.uow:
            if self.uow.users.filter_one(username=username):
                raise AuthUserError("username taken")

            self.uow.users.add(user)

            collaborator.user_id = user.id
            self.uow.collaborators.add(collaborator)
            self.uow.commit()

            user_dto = AuthUserDTO.from_domain(user)
            collaborator_dto = CollaboratorDTO.from_domain(collaborator)
        return user_dto, collaborator_dto
