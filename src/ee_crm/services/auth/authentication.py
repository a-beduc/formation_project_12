"""Authentication service responsible for validating user credentials.

The service use a unit of work (uow) abstraction to interrogate data
persistence layer.

Class
    AuthenticationService   # Service class
"""
from ee_crm.exceptions import AuthenticationError


class AuthenticationService:
    """Service to perform the log-in flow.

    Attributes:
        uow (AbstractUnitOfWork): Unit of work exposing the 'users' and
            'collaborators' repositories.
    """
    def __init__(self, uow):
        self.uow = uow

    @staticmethod
    def verify_identity(uow, username, plain_password):
        """Retrieve a user and validate the supplied credentials.
        This method should be used at the service layer only.

        Args
            uow (AbstractUnitOfWork): Injected open unit of work.
            username (str): Given username.
            plain_password (str): Given password.

        Return
            User: Domain entity representing the user.

        Raises:
            AuthenticationError: If the supplied credentials are
                invalid.
        """
        user = uow.users.filter_one(username=username)
        if user is None:
            err = AuthenticationError('No user found')
            err.tips = (f"No user with the username \"{username}\" found in "
                        f"the database.")
            raise err
        user.verify_password(plain_password)
        return user

    def authenticate(self, username, plain_password):
        """Authenticate a user from supplied credentials and return the
        JWT ready payload.

        Args
            username (str): Given username.
            plain_password (str): Given password.

        Returns
            dict: JWT payload.
        """
        with self.uow:
            user = self.verify_identity(self.uow, username, plain_password)
            collaborator = self.uow.collaborators.filter_one(user_id=user.id)
            return {
                "sub": user.username,
                "c_id": collaborator.id,
                "role": collaborator.role,
                "name": f"{collaborator.first_name} {collaborator.last_name}"
            }
