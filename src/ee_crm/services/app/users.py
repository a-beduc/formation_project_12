from ee_crm.services.dto import AuthUserDTO
from ee_crm.services.auth.authentication import AuthenticationService


class UserServiceError(Exception):
    pass


class UserService:
    def __init__(self, uow):
        self.uow = uow
        self.error_cls = UserServiceError

    def retrieve(self, user_id):
        with self.uow:
            user = self.uow.users.get(user_id)
            if user is None:
                raise self.error_cls(f"User not found with id {user_id}")
            return (AuthUserDTO.from_domain(user),)

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
