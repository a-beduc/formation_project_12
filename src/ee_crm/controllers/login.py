from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork
from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.auth.jwt_handler import (
    create_and_store_tokens, verify_token, BadToken)


def login(username, plain_password):
    uow = SqlAlchemyUnitOfWork()
    service = AuthenticationService(uow)
    payload = service.authenticate(username, plain_password)
    create_and_store_tokens(payload)


def check_token():
    try:
        return verify_token()
    except BadToken:
        return None
