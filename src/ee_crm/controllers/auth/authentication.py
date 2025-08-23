"""The functions responsible for initiating and starting the services
and flows responsible for the authentication of users.

Functions
    login   # Verify credentials then store a JWT to confirm identity.
    logout  # Clear the stored JWT.
"""
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.auth.jwt_handler import create_and_store_tokens, \
    wipe_tokens


def login(username, plain_password):
    """Verify credentials then store a JWT to confirm identity.

    Args
        username (str): Username.
        plain_password (str): The plain-text password.
    """
    uow = DEFAULT_UOW()
    service = AuthenticationService(uow)
    payload = service.authenticate(username, plain_password)
    create_and_store_tokens(payload)


def logout():
    """Clear the stored JWT."""
    wipe_tokens()
