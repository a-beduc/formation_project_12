from functools import wraps, update_wrapper
from inspect import signature, Parameter

from ee_crm.exceptions import AuthorizationDenied, BadToken

from ee_crm.services.app.clients import ClientService
from ee_crm.services.app.contracts import ContractService
from ee_crm.services.app.events import EventService
from ee_crm.services.auth.jwt_handler import verify_token
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork


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
    except BadToken:
        raise AuthorizationDenied('Authentication invalid')


@predicate
def is_management(ctx):
    return ctx['auth']['role'] == 3


@predicate
def is_sales(ctx):
    return ctx['auth']['role'] == 4


@predicate
def is_support(ctx):
    return ctx['auth']['role'] == 5


@predicate
def is_self(ctx):
    return ctx.get('pk', None) == ctx['auth']['c_id']


@predicate
def is_client_associated_salesman(ctx):
    client_id = ctx.get('pk', None)
    logged_u_id = ctx['auth']['c_id']
    service = ClientService(SqlAlchemyUnitOfWork())
    salesman_id = service.retrieve(client_id)[0].salesman_id
    return salesman_id == logged_u_id


@predicate
def contract_has_salesman(ctx):
    contract_id = ctx.get('pk', None)
    service = ContractService(SqlAlchemyUnitOfWork())
    s_id = service.retrieve_associated_client(contract_id)[0].salesman_id
    return s_id is not None


@predicate
def is_contract_associated_salesman(ctx):
    contract_id = ctx.get('pk', None)
    logged_u_id = ctx['auth']['c_id']
    service = ContractService(SqlAlchemyUnitOfWork())
    s_id = service.retrieve_associated_client(contract_id)[0].salesman_id
    return s_id == logged_u_id


@predicate
def contract_is_signed(ctx):
    contract_id = ctx.get('pk', None)
    service = ContractService(SqlAlchemyUnitOfWork())
    return service.retrieve(contract_id)[0].signed


@predicate
def event_has_support(ctx):
    event_id = ctx.get('pk', None)
    service = EventService(SqlAlchemyUnitOfWork())
    return service.retrieve(event_id)[0].supporter_id is not None


@predicate
def is_event_associated_support(ctx):
    event_id = ctx.get('pk', None)
    logged_u_id = ctx['auth']['c_id']
    service = EventService(SqlAlchemyUnitOfWork())
    return service.retrieve(event_id)[0].supporter_id == logged_u_id


@predicate
def is_event_associated_salesman(ctx):
    event_id = ctx.get('pk', None)
    logged_u_id = ctx['auth']['c_id']
    service = EventService(SqlAlchemyUnitOfWork())
    salesman_id = service.retrieve_associated_client(event_id)[0].salesman_id
    return salesman_id == logged_u_id


def _map_func_signature_and_value(func, *args, **kwargs):
    # source : https://www.geeksforgeeks.org/python-get-function-signature/
    ctx = {}
    # get func positional args name
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]

    # map func args name with values (not defaults one)
    # map the rest of args in a 'args' keyword
    args_dict = dict(zip(arg_names, args))
    args_dict['args'] = args[len(arg_names):]

    # map the defaults values of positional args if not given
    defaults_args_value = func.__defaults__
    if defaults_args_value:
        defaults_arg_names = dict(zip(arg_names, defaults_args_value))
        for name, default in defaults_arg_names.items():
            args_dict.setdefault(name, default)
    ctx.update(args_dict)

    # map the keyword arguments if not given
    for key, default in (func.__kwdefaults__ or {}).items():
        kwargs.setdefault(key, default)
    ctx.update(kwargs)

    return ctx


def _accept_kwargs(func):
    # https://docs.python.org/3/library/inspect.html#inspect.Parameter.kind
    sig = signature(func)
    return any(p.kind == Parameter.VAR_KEYWORD for
               p in sig.parameters.values())


def permission(_func=None, *, requirements=None, kw_auth=True):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth = is_authenticated()
            ctx = {'auth': auth}

            if requirements is not None:
                ctx.update(
                    _map_func_signature_and_value(func, *args, **kwargs))
            # print(ctx)
            # exit()
                if not requirements(ctx):
                    raise AuthorizationDenied(
                        f'Permission error in {requirements}')

            # if flag is raised and func accept **kwargs can pass payload
            if kw_auth and _accept_kwargs(func):
                kwargs['auth'] = auth

            return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)
