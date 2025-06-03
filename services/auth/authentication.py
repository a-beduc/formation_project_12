from domain.model import AuthUserError


class AuthenticationError(Exception):
    pass


class AuthenticationService:
    def __init__(self, uow):
        self.uow = uow

    @staticmethod
    def verify_identity(uow, username, plain_password):
        user = uow.users.filter_one(username=username)
        if user is None:
            raise AuthenticationError(f"User not found with {username}")

        try:
            user.verify_password(plain_password)
        except AuthUserError:
            raise AuthenticationError("Password mismatch")

        return user

    def authenticate(self, username, plain_password):
        with self.uow:
            user = self.verify_identity(self.uow, username, plain_password)

            collaborator = self.uow.collaborators.filter_one(user_id=user.id)
            return {
                "sub": user.username,
                "c_id": collaborator.id,
                "role": collaborator.role,
                "name": f"{collaborator.first_name} {collaborator.last_name}"
            }
