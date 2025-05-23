from services.unit_of_work import SqlAlchemyUnitOfWork
from services import jwt_handler, authentication


def login(username, plain_password):
    uow = SqlAlchemyUnitOfWork()
    data = authentication.authenticate(uow, username, plain_password)
    jwt_handler.create_and_store_tokens(data)


def check_token():
    try:
        return jwt_handler.verify_token()
    except jwt_handler.BadToken:
        return None
