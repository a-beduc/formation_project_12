from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_string
from ee_crm.exceptions import UserManagerError
from ee_crm.services.app.collaborators import CollaboratorService
from ee_crm.services.app.users import UserService
from ee_crm.services.auth.authentication import AuthenticationService


class UserManager(BaseManager):
    label = "User"
    _validate_types_map = {
        "id": verify_positive_int,
        "username": verify_string,
    }
    _default_service = UserService(DEFAULT_UOW())
    error_cls = UserManagerError

    @permission("user:read")
    def read(self, pk=None, filters=None, sort=None):
        return super().read(pk=pk, filters=filters, sort=sort)

    @permission("user:whoami")
    def who_am_i(self, **kwargs):
        uow = DEFAULT_UOW()
        c_id = kwargs['auth']['c_id']
        coll = CollaboratorService(uow).retrieve(c_id)[0]
        user = self.service.retrieve(coll.user_id)[0]
        return user, coll

    @permission("user:modify_username_own")
    def update_username(self, old_username, plain_password, new_username,
                        **kwargs):
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
        if not plain_password_1 == plain_password_2:
            err = cls.error_cls("passwords do not match")
            err.tips("The given passwords do not match, verify any typo and "
                     "try again")
            raise err
