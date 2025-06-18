from ee_crm.domain.model import AuthUser
from ee_crm.exceptions import UserServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.dto import AuthUserDTO


class UserService(BaseService):
    def __init__(self, uow):
        super().__init__(
            uow,
            AuthUser,
            AuthUserDTO,
            UserServiceError,
            "users"
        )

    def create(self, **obj_value):
        raise UserServiceError("Can't create user directly, "
                               "use appropriate methods.")

    def remove(self, obj_id):
        raise UserServiceError("Can't delete user directly, "
                               "use appropriate methods.")

    def modify(self, obj_id, **kwargs):
        raise UserServiceError("Can't update user directly, "
                               "use appropriate methods.")

    def modify_username(self, old_username, plain_password, new_username):
        with self.uow:
            user_with_username = self.uow.users.filter_one(
                username=new_username)
            if user_with_username is not None:
                raise self.error_cls(f"User with username {new_username} "
                                     f"already exists")
            user = AuthenticationService.verify_identity(self.uow,
                                                         old_username,
                                                         plain_password)
            user.username = new_username
            self.uow.commit()

    def modify_password(self, username, old_plain_password,
                        new_plain_password):
        with self.uow:
            user = AuthenticationService.verify_identity(self.uow, username,
                                                         old_plain_password)
            user.set_password(new_plain_password)
            self.uow.commit()
