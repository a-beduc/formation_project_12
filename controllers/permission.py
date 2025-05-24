from controllers.login import check_token
from functools import wraps
from inspect import signature, Parameter


def is_authenticated():
    payload = check_token()
    if payload is None:
        raise PermissionError('Authentication invalid')
    return payload


def is_management(ctx):
    return ctx['auth']['role'] == 3


def is_sales(ctx):
    return ctx['auth']['role'] == 4


def is_support(ctx):
    return ctx['auth']['role'] == 5


# Implement later, uow should be in services layer

# def is_client_salesman(ctx):
#     uow = ctx['uow']
#     return (uow.clients.get(ctx['client_id']).salesman_id ==
#             ctx['auth']['c_id'])
#
#
# def is_contract_salesman(ctx):
#     uow = ctx['uow']
#     return uow.contracts.get_client_from_contract(ctx['contract_id']).salesman_id == ctx['auth']['c_id']
#
#
# def is_event_support(ctx):
#     uow = ctx['uow']
#     return uow.events.get(ctx['event_id']).support_id == ctx['auth']['c_id']


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


def _verify_requirements(ctx, requirements):
    for group in requirements:
        if not any(rule(ctx) for rule in group):
            raise PermissionError(
                f'Permission error in {[perm.__name__ for perm in group]}')


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

            if requirements:
                ctx.update(
                    _map_func_signature_and_value(func, *args, **kwargs))

                _verify_requirements(ctx, requirements)

            # if flag is raised and func accept **kwargs can pass payload
            if kw_auth and _accept_kwargs(func):
                kwargs['auth'] = auth

            return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


# def authenticated(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         payload = is_authenticated()
#         if payload is None:
#             raise (Exception('Need authentication'))
#         kwargs['auth'] = payload
#         return func(*args, **kwargs)
#
#     return wrapper
#
#
# def old_permission(requirements):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#
#             for group in requirements:
#                 if not any(rule(kwargs) for rule in group):
#                     raise Exception(
#                         f'Permission error in {
#                           [perm.__name__ for perm in group]}')
#             # kwargs cleanup
#             for key in perms_key:
#                 kwargs.pop(key, None)
#             return func(*args, **kwargs)
#
#         return wrapper
#
#     return decorator
