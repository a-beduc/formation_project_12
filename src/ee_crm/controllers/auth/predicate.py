from functools import update_wrapper

from ee_crm.domain.model import Role
from ee_crm.exceptions import BadToken, AuthorizationDenied
from ee_crm.services.auth.jwt_handler import verify_token


class P:
    """
    https://stackoverflow.com/questions/9184632/pointfree-function-combination-in-python
    """
    def __init__(self, func, label=None):
        self.pred = func
        self.func_name = label or func.__name__

    def __call__(self, ctx):
        return self.pred(ctx)

    def __and__(self, other):
        def func(ctx):
            return self(ctx) and other(ctx)
        return P(func, label=f'({self.func_name} and {other.func_name})')

    def __or__(self, other):
        def func(ctx):
            return self(ctx) or other(ctx)
        return P(func, label=f'({self.func_name} or {other.func_name})')

    def __invert__(self):
        def func(ctx):
            return not self(ctx)
        return P(func, label=f'not {self.func_name}')

    def __repr__(self):
        return self.func_name


def predicate(func):
    result = P(func)
    update_wrapper(result, func)
    return result


def is_authenticated():
    try:
        return verify_token()
    except BadToken as e:
        err = AuthorizationDenied('Authentication invalid')
        err.tips = e.tips
        raise err


@predicate
def is_management(ctx):
    return ctx['auth']['role'] == Role.MANAGEMENT


@predicate
def is_sales(ctx):
    return ctx['auth']['role'] == Role.SALES


@predicate
def is_support(ctx):
    return ctx['auth']['role'] == Role.SUPPORT


@predicate
def is_self(ctx):
    return ctx.get('pk', None) == ctx['auth']['c_id']


@predicate
def client_has_salesman(ctx):
    client_id = ctx.get('pk', None)
    service = ctx['perm_service']
    salesman_id = service.get_client_associated_salesman(client_id)
    return salesman_id is not None


@predicate
def is_client_associated_salesman(ctx):
    client_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    salesman_id = service.get_client_associated_salesman(client_id)
    return salesman_id == logged_user_id


@predicate
def contract_has_salesman(ctx):
    contract_id = ctx.get('pk', None)
    service = ctx['perm_service']
    salesman_id = service.get_contract_associated_salesman(contract_id)
    return salesman_id is not None


@predicate
def is_contract_associated_salesman(ctx):
    contract_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    salesman_id = service.get_contract_associated_salesman(contract_id)
    return salesman_id == logged_user_id


@predicate
def contract_is_signed(ctx):
    contract_id = ctx.get('pk', None)
    service = ctx['perm_service']
    signed = service.get_contract_signed(contract_id)
    # since signed is a type bool, no assert
    return signed


@predicate
def event_has_support(ctx):
    event_id = ctx.get('pk', None)
    service = ctx['perm_service']
    supporter_id = service.get_event_support(event_id)
    return supporter_id is not None


@predicate
def is_event_associated_support(ctx):
    event_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    supporter_id = service.get_event_support(event_id)
    return supporter_id == logged_user_id


@predicate
def is_event_associated_salesman(ctx):
    event_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    salesman_id = service.get_event_associated_salesman(event_id)
    return salesman_id == logged_user_id
