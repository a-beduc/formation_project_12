"""Service layer responsible for Collaborator domain entities.

Classes
    CollaboratorService # Business operations for collaborators.
"""
from ee_crm.domain.model import AuthUser, Collaborator, Role
from ee_crm.exceptions import CollaboratorServiceError, CollaboratorDomainError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import CollaboratorDTO


class CollaboratorService(BaseService):
    """Manage collaborators, the linked user account and their roles.

    Attributes
        uow (AbstractUnitOfWork): Unit of work exposing repositories.
    """
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
        """Convert a role input into the integer enum representing Role.

        Args
            role (str|int): Input role.
            strict (bool): When True, raise a CollaboratorServiceError,
                otherwise a negative value is sent back to the caller
                that can treat it as a no-match.

        Returns
            Role: The integer enum representing the role.
        """
        if strict:
            return Role.sanitizer(role)
        try:
            return Role.sanitizer(role)
        except CollaboratorDomainError:
            # used to filter out every role for queries with invalid
            # Role input
            return -1

    def create(self, username, plain_password, role=1, **kwargs):
        """Create a collaborator and its associated user account.

        Args
            username (str): Username for the user account.
            plain_password (str): Password for the user account.
            role (str|int|Role): The role of the collaborator.
            **kwargs (Any): Additional keyword arguments to create the
                collaborator entity.

        Returns
            Tuple[CollaboratorDTO]: A single element tuple containing
                the collaborator dto for the newly created entity.
        """
        with self.uow:
            if self.uow.users.filter_one(username=username):
                err = self.error_cls("username taken")
                err.tips = (f"The username {username} is taken, select a "
                            f"different one and try again.")
                raise err
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

            return (self.dto_cls.from_domain(collaborator),)

    def remove(self, collaborator_id=None, user_id=None):
        """Remove a collaborator and its associated user account from
        the persistence layer. It can be done by giving either the
        primary key of the collaborator or the primary key of the user.

        Args
            collaborator_id (int): Primary key of the collaborator to
                remove.
            user_id (int): Primary key of the user to remove.
        """
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
        """Assign a role to a collaborator.

        Args
            collaborator_id (int): Primary key of the collaborator.
            role (int|Role): The role of the collaborator.
        """
        with self.uow:
            roles = {
                Role.DEACTIVATED,
                Role.MANAGEMENT,
                Role.SALES,
                Role.SUPPORT
            }
            if role not in roles:
                err = CollaboratorServiceError(f"Invalid role: {role}")
                err.tips = (f"Invalid role {role}, the role can be one of the "
                            f"following : {', '.join(r.name for r in roles)}")
                raise err
            collaborator = self._repo.get(collaborator_id)
            collaborator.role = role
            self.uow.commit()
