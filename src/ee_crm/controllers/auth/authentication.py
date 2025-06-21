from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.auth.jwt_handler import create_and_store_tokens, \
    wipe_tokens


def login(username, plain_password):
    uow = DEFAULT_UOW()
    service = AuthenticationService(uow)
    payload = service.authenticate(username, plain_password)
    create_and_store_tokens(payload)


def logout():
    wipe_tokens()
