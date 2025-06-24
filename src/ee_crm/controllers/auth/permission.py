from functools import wraps
from inspect import signature, Parameter

from ee_crm.controllers.auth.predicate import is_authenticated
from ee_crm.controllers.auth.rbac import PERMS
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.domain.model import Role
from ee_crm.exceptions import AuthorizationDenied
from ee_crm.services.auth.permissions import PermissionService


def _map_func_signature_and_value(func, *args, **kwargs):
    # source : https://www.geeksforgeeks.org/python-get-function-signature/
    ctx = {}
    # get func positional args name before *args, **kwargs
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]

    # map func args name with values (not defaults one)
    # map the rest of args in a 'args' keyword
    args_dict = dict(zip(arg_names, args))
    args_dict['args'] = args[len(arg_names):]

    # map the defaults values of positional args if not given
    # func(a, b, c=10, d=20) will return (10, 20)
    defaults_args_value = func.__defaults__
    if defaults_args_value:
        # func(a, b, c=10, d=20) will return ("c", "d")
        defaults_arg_names = arg_names[-len(defaults_args_value):]
        defaults_arg_names_and_value = (
            dict(zip(defaults_arg_names, defaults_args_value)))
        for name, default in defaults_arg_names_and_value.items():
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


def permission(*rbac, abac=None, kw_auth=True):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # AUTH
            auth = is_authenticated()
            ctx = {'auth': auth}

            # RBAC
            role_name = Role(auth['role']).name
            any_perm = set(rbac).intersection(PERMS[role_name])
            if not any_perm:
                err = AuthorizationDenied(
                    f'Permission error (RBAC) in {rbac}.')
                err.tips = \
                    (f"This command isn't available to your account, "
                     f"you didn't have a Role with the necessary "
                     f"permissions. This command is available to Roles "
                     f"with the permissions : {rbac}")
                raise err

            # ABAC
            if abac is not None:
                ctx.update(
                    _map_func_signature_and_value(func, *args, **kwargs))

                # not thrilled with opening context manager in Controller
                with DEFAULT_UOW() as uow:
                    service = PermissionService(uow)
                    ctx["perm_service"] = service

                    if not abac(ctx):
                        err = AuthorizationDenied(
                            f'Permission error (ABAC) in {abac}')
                        err.tips = \
                            (f"This command isn't available to your account, "
                             f"you didn't satisfy at least one of the "
                             f"following required authorizations : "
                             f"{abac}")
                        raise err

            # if flag is raised and func accept **kwargs can pass payload
            if kw_auth and _accept_kwargs(func):
                kwargs['auth'] = auth

            return func(*args, **kwargs)

        return wrapper
    return decorator
