from services.dto import AuthUserDTO


class UserServiceError(Exception):
    pass


class UserService:
    def __init__(self, uow):
        self.uow = uow

    def get_user_by_id(self, user_id):
        with self.uow:
            user = self.uow.users.get(user_id)
            if user is None:
                raise UserServiceError(f"User not found with {user_id}")
            return AuthUserDTO.from_domain(user)
