from domain.model import AuthUserError


class AuthenticationError(Exception):
    pass


class AuthenticationService:
    def __init__(self, uow):
        self.uow = uow

    def authenticate(self, username, plain_password):
        with self.uow:
            user = self.uow.users.filter_one(username=username)
            if user is None:
                raise AuthenticationError(f"User not found with {username}")

            try:
                user.verify_password(plain_password)
            except AuthUserError:
                raise AuthenticationError("Password mismatch")

            collaborator = self.uow.collaborators.filter_one(user_id=user.id)
            return {
                "sub": user.username,
                "c_id": collaborator.id,
                "role": collaborator.role_id,
                "name": f"{collaborator.first_name} {collaborator.last_name}"
            }

    def change_password(self, username, old_plain_password,
                        new_plain_password):
        with self.uow:
            user = self.uow.users.filter_one(username=username)
            if user is None:
                raise AuthenticationError(f"User not found with {username}")

            try:
                user.verify_password(old_plain_password)
            except AuthUserError:
                raise AuthenticationError("Password mismatch")

            user.set_password(new_plain_password)

            self.uow.commit()
