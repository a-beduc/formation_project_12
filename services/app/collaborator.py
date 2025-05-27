from domain.model import AuthUser, Collaborator, AuthUserError
from services import dto


class CollaboratorServiceError(Exception):
    pass


class CollaboratorService:
    # need to sanitize user input at controller layer
    def __init__(self, uow):
        self.uow = uow

    def create_collaborator_with_user(
            self,
            *,
            username,
            plain_password,
            last_name=None,
            first_name=None,
            email=None,
            phone_number=None,
            role_id=1):

        AuthUser.validate_password(plain_password)
        AuthUser.validate_username(username)

        user = AuthUser.build_user(username, plain_password)
        collaborator = Collaborator(
            last_name=last_name,
            first_name=first_name,
            email=email,
            phone_number=phone_number,
            role_id=role_id,
            user_id=None,
        )

        with self.uow:
            if self.uow.users.get_by_username(username):
                raise AuthUserError("username taken")

            self.uow.users.add(user)

            collaborator.user_id = user.id
            self.uow.collaborators.add(collaborator)
            self.uow.commit()

            user_dto = dto.AuthUserDTO.from_domain(user)
            collaborator_dto = dto.CollaboratorDTO.from_domain(collaborator)

        return user_dto, collaborator_dto

    def get_collaborator_from_user_id(self, user_id):
        with self.uow:
            collaborator = self.uow.collaborators.get_by_user_id(user_id)
            if collaborator is None:
                raise CollaboratorServiceError("Collaborator not found")
            return dto.CollaboratorDTO.from_domain(collaborator)

    def get_collaborator_by_id(self, collaborator_id):
        with self.uow:
            collaborator = self.uow.collaborators.get(collaborator_id)
            try:
                return dto.CollaboratorDTO.from_domain(collaborator)
            except AttributeError:
                raise CollaboratorServiceError("Collaborator not found")

    def get_list_of_collaborators(self, filter_by_role_id=None):
        with self.uow:
            if filter_by_role_id is None:
                l_c = self.uow.collaborators.list()
            else:
                l_c = self.uow.collaborators.filter_by_role(filter_by_role_id)
            list_of_coll = [dto.CollaboratorDTO.from_domain(c) for c in l_c]
            return list_of_coll

    def delete_collaborator(self, collaborator_id):
        with self.uow:
            self.uow.collaborators.delete(collaborator_id)
            self.uow.commit()

    def update_collaborator(self, collaborator_id, **kwargs):
        updatable_fields = Collaborator.get_updatable_fields()
        with self.uow:
            collaborator = self.uow.collaborators.get(collaborator_id)
            update_value = {k: kwargs.get(k, None) for k in updatable_fields}
            for k, v in update_value.items():
                if v is not None:
                    setattr(collaborator, k, v)
            self.uow.commit()
