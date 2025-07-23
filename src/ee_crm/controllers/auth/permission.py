"""Permission decorator.

This module centralise the logic needed for allowing a function to be
executed. It checks for 'authentication', 'role-based access control'
(RBAC) and 'attribute-based access control' (ABAC).

Functions
    permission  # combine auth, rbac and abac in one decorator.
"""
from functools import wraps
from inspect import signature, Parameter

from ee_crm.controllers.auth.predicate import is_authenticated
from ee_crm.controllers.auth.rbac import PERMS
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.domain.model import Role
from ee_crm.exceptions import AuthorizationDenied
from ee_crm.services.auth.permissions import PermissionService


def _map_func_signature_and_value(func, *args, **kwargs):
    """This helper map the given args and kwargs to the signature of
    a function, in order to dynamically create a context dictionary
    that contains parameters mapped to keywords.

    In essence, this function forces all the parameters given to a
    function to become keyword-value pair in a dictionary.
    To follow the logic of the helper, use the in-line comments.

    Example
        def ->
        func(a, b, c=10, d=20, e=30, f=40, *args, kwa_a=1, kwa_b=2,
             **kwargs)

        call ->
        func(1, 2, kwa_a=20, kwa_c=50)

        return ->
        {"a": 1, "b": 2, "c": 10, "d": 20, "e": 30, "f": 40, "args": (),
         "kwa_a": 20, "kwa_b": 2, "kwa_c": 50}

    Args
        func (callable): A function.
        *args (tuple): Positional arguments given to the function.
        **kwargs (dict): Keyword arguments given to the function.

    Returns
        dict: A context dictionary that contains keywords mapped to
            parameters.

    References:
        Inspiration from the 'Using decorators' of a geeksforgeeks page.
        https://www.geeksforgeeks.org/python-get-function-signature/
    """
    ctx = {}

    # get func positional args name before *args, **kwargs
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]

    # map func args name with values (not defaults one)
    # map the rest of args in an 'args' keyword
    args_dict = dict(zip(arg_names, args))
    args_dict['args'] = args[len(arg_names):]

    # map the defaults values of positional args if not given
    # func(a, b, c=10, d=20) will return (10, 20)
    defaults_args_value = func.__defaults__
    if defaults_args_value:
        # func(a, b, c=10, d=20) will return ("c", "d")
        defaults_arg_names = arg_names[-len(defaults_args_value):]

        # func(a, b, c=10, d=20) will return {"c": 10, "d": 20}
        defaults_arg_names_and_value = (
            dict(zip(defaults_arg_names, defaults_args_value)))

        # add the key-value pair for args with default value if not
        # redeclared.
        for name, default in defaults_arg_names_and_value.items():
            args_dict.setdefault(name, default)

    ctx.update(args_dict)

    # map the keyword arguments with default value if not redeclared.
    for key, default in (func.__kwdefaults__ or {}).items():
        kwargs.setdefault(key, default)

    ctx.update(kwargs)

    return ctx


def _accept_kwargs(func):
    """Verify that the given function accept additional keyword
    arguments

    Args
        func (callable): The function

    Returns
        bool: Whether the given function accept additional keyword.

    References
        https://docs.python.org/3/library/inspect.html#inspect.Parameter.kind
    """
    sig = signature(func)
    return any(p.kind == Parameter.VAR_KEYWORD for
               p in sig.parameters.values())


def permission(*rbac, abac=None, kw_auth=True):
    """Decorator that handle the operation needed for the permission
    system of the application.

    It follows the pattern:
        * (AUTH) Verify if user is authenticated.
        * (RBAC) Verify if the user's role allows it to perform action.
        * (ABAC) Verify if resource based permissions are respected.
        * if flag is raised, pass the JWT payload to the wrapped func.

    Args
        *rbac (tuple[str]): The packed RBAC tags. If the user respect
            any of the tags it passes the perms.
        abac (ee_crm.controllers.auth.predicate.P): Predicate construct.
        kw_auth (bool): Whether the user payload need to be given to
            the wrapped func.

    Returns
        func(): The wrapped function, called with its parameters.

    References
        https://realpython.com/primer-on-python-decorators/
    """
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

                # TODO: Ideally the uow should be opened deeper in the
                #  service layer. The current design avoid to open
                #  multiple uow. Need refactoring/rework.
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
