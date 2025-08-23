"""Service layer responsible for AuthUser domain entities.
It blocks some basic CRUD implementation to force the use of more
robust method to interact with this resource.

Classes
    UserService # Business operations for users.
"""
from ee_crm.domain.model import AuthUser
from ee_crm.exceptions import UserServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.dto import AuthUserDTO


class UserService(BaseService):
    """Manage users and the operations to modify username and password.

    Attributes
        uow (AbstractUnitOfWork): Unit of work exposing repositories.
    """
    def __init__(self, uow):
        super().__init__(
            uow,
            AuthUser,
            AuthUserDTO,
            UserServiceError,
            "users"
        )

    def create(self, **obj_value):
        """Block the create method, to create a new user, refer to the
        CollaboratorService.

        Raises
            UserServiceError: If the method is called
        """
        raise UserServiceError("Can't create user directly, "
                               "use appropriate methods.")

    def remove(self, obj_id):
        """Block the delete method, to delete a user, refer to the
        CollaboratorService.

        Raises
            UserServiceError: If the method is called
        """
        raise UserServiceError("Can't delete user directly, "
                               "use appropriate methods.")

    def modify(self, obj_id, **kwargs):
        """Block the update method, use appropriate methods to modify
        the username of the password.

        Raises
            UserServiceError: If the method is called
        """
        raise UserServiceError("Can't update user directly, "
                               "use appropriate methods.")

    def modify_username(self, old_username, plain_password, new_username):
        """Proper method to modify the username of a user account.
        Verify identity before proceeding with the request.

        Args
            old_username (str): The old username.
            plain_password (str): The plain-text password.
            new_username (str): The new username.

        Raises
            UserServiceError: If the new username already exist in the
                persistence layer.
        """
        with self.uow:
            user_with_username = self.uow.users.filter_one(
                username=new_username)
            if user_with_username is not None:
                err = self.error_cls(f"User with username {new_username} "
                                     f"already exists")
                err.tips = (f"The username {new_username} is taken, select a "
                            f"different one and try again.")
                raise err
            user = AuthenticationService.verify_identity(self.uow,
                                                         old_username,
                                                         plain_password)
            user.username = new_username
            self.uow.commit()

    def modify_password(self, username, old_plain_password,
                        new_plain_password):
        """Proper method to modify the password of a user account.
        Verify identity before proceeding with the request.

        Args
            username (str): Username.
            old_plain_password (str): The plain-text old password.
            new_plain_password (str): The plain-text new password.
        """
        with self.uow:
            user = AuthenticationService.verify_identity(self.uow, username,
                                                         old_plain_password)
            user.set_password(new_plain_password)
            self.uow.commit()
