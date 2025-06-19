from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.auth.jwt_handler import create_and_store_tokens, \
    wipe_tokens
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork


def login(username, plain_password):
    uow = SqlAlchemyUnitOfWork()
    service = AuthenticationService(uow)
    payload = service.authenticate(username, plain_password)
    create_and_store_tokens(payload)


def logout():
    wipe_tokens()
