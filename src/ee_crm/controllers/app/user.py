"""Controller class for the User resource operations.

The create/update/delete methods should never be called and have been
overridden as a safety measure.

Classes
    UserManager # It expands BaseManager to add user specific
                # operations.
"""
from typing import override

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_string
from ee_crm.exceptions import UserManagerError
from ee_crm.services.app.collaborators import CollaboratorService
from ee_crm.services.app.users import UserService
from ee_crm.services.auth.authentication import AuthenticationService


class UserManager(BaseManager):
    """Controller for User resource.

    Inherits from BaseManager, only public attributes differences are
    documented below.

    Attributes
        label: "User"
        error_cls: UserManagerError
        service (ee_crm.services.app.users.UserService): The service
            class to start operations with.
    """
    label = "User"
    _validate_types_map = {
        "id": verify_positive_int,
        "username": verify_string,
    }
    _default_service = UserService(DEFAULT_UOW())
    error_cls = UserManagerError

    @override
    def create(self, **kwargs):
        """Raise an error if used, user should be created through the
        CollaboratorManager to assure creation of the two resources in
        tandem.

        Raises
            UserManagerError: If used.
        """
        err = self.error_cls("Can't create user directly, "
                             "use appropriate methods.")
        err.tips = ("You can't create a user manually, please use "
                    "appropriate commands.")
        raise err

    @override
    @permission("user:read")
    def read(self, pk=None, filters=None, sort=None):
        """See BaseManager.read"""
        return super().read(pk=pk, filters=filters, sort=sort)

    @override
    def update(self, *args, **kwargs):
        """Raise an error if used, contract should be modified through
        specific methods.

        Raises
            UserManagerError: If used.
        """
        err = self.error_cls("Can't update user directly, "
                             "use appropriate methods.")
        err.tips = ("You can't update a user directly, please use "
                    "appropriate commands.")
        raise err

    @override
    def delete(self, *args, **kwargs):
        """Raise an error if used, contract should be modified through
        specific methods.

        Raises
            UserManagerError: If used.
        """
        err = self.error_cls("Can't delete user directly, "
                             "use appropriate methods.")
        err.tips = ("You can't delete a user directly, please use "
                    "appropriate commands.")
        raise err

    @permission("user:whoami")
    def who_am_i(self, **kwargs):
        """Method to retrieve the information about the logged in user

        Args
            kwargs (dict): extra arguments, like JWT payload.

        Returns
            tuple[AuthUserDTO, CollaboratorDTO]: A tuple containing the
                data transfer object of the user and linked collaborator
                data.
        """
        uow = DEFAULT_UOW()
        c_id = kwargs['auth']['c_id']
        coll = CollaboratorService(uow).retrieve(c_id)[0]
        user = self.service.retrieve(coll.user_id)[0]
        return user, coll

    @permission("user:modify_username_own")
    def update_username(self, old_username, plain_password, new_username,
                        **kwargs):
        """Method to update the username of the logged-in user.
        It needs credentials to verify identity before processing with
        request.

        Args
            old_username (str): The old username of the user to verify
                identity.
            plain_password (str): The password of the user account.
            new_username (str): The new username of the user.
            kwargs (dict): extra arguments, like JWT payload.

        Raises
            UserManagerError: If wrong credentials are provided.
        """
        service_auth = AuthenticationService(DEFAULT_UOW())
        payload = service_auth.authenticate(old_username, plain_password)

        if not payload['c_id'] == kwargs['auth']['c_id']:
            err = self.error_cls("You can't modify someone else username.")
            err.tips = ("Trying to modify someone else username is forbidden, "
                        "log out and log back in as the user you want to "
                        "modify")
            raise err
        self.service.modify_username(str(old_username),
                                     str(plain_password),
                                     str(new_username))

    @permission("user:modify_password_own")
    def update_password(self, username, old_plain_password,
                        new_plain_password, **kwargs):
        """Method to update the password of the logged-in user.
        It needs credentials to verify identity before processing with
        request.

        Args
            username (str): The username of the user.
            old_plain_password (str): The current password of the user
                account
            new_plain_password (str): The new password of the user
                account.
            kwargs (dict): extra arguments, like JWT payload.

        Raises
            UserManagerError: If wrong credentials are provided.
        """
        service_auth = AuthenticationService(DEFAULT_UOW())
        payload = service_auth.authenticate(username, old_plain_password)

        if not payload['c_id'] == kwargs['auth']['c_id']:
            err = self.error_cls("You can't modify someone else password.")
            err.tips = ("Trying to modify someone else password is forbidden, "
                        "log out and log back in as the user you want to "
                        "modify")
            raise err
        self.service.modify_password(str(username),
                                     str(old_plain_password),
                                     str(new_plain_password))

    @classmethod
    def verify_plain_password_match(cls, plain_password_1, plain_password_2):
        """Helper to verify if two password matches, used for creation.

        Args
            plain_password_1 (str): The password.
            plain_password_2 (str): Ideally, the same password.

        Raises
            UserManagerError: If the password does not match.
        """
        if not plain_password_1 == plain_password_2:
            err = cls.error_cls("passwords do not match")
            err.tips = ("The given passwords do not match, verify any typo "
                        "and try again")
            raise err
