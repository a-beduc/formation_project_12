from ee_crm.exceptions import AuthenticationError


class AuthenticationService:
    def __init__(self, uow):
        self.uow = uow

    @staticmethod
    def verify_identity(uow, username, plain_password):
        user = uow.users.filter_one(username=username)
        if user is None:
            err = AuthenticationError('No user found')
            err.tips = (f"No user with the username \"{username}\" found in "
                        f"the database.")
            raise err
        user.verify_password(plain_password)
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
