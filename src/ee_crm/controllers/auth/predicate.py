"""Implementation of fine-grained Attribute Based Access Control (ABAC).

Boolean functions are wrapped in a class P and combined with the bitwise
operators '&', '|' and '~'. P forms predicates that when called will
inject the parameters to the wrapped function to evaluate their
truthiness.

Example
    To express:
        func_one and func_two or not func_three

    Will result in:
        P(P(P(func_one) & P(func_two)) | P(~P(func_three)))

    When called, the ctx will be injected in P until it reaches bool
    functions:
        P(P(P(func_one) & P(func_two)) | P(~P(func_three)))(ctx)
        -> bool

Classes
    P   # Wrapper around a boolean function.

Functions
    predicate                       # Decorator that returns a P.
    is_authenticated                # Validate the stored JWT.
    is_management                   # Check MANAGEMENT role.
    is_sales                        # Check SALES role.
    is_support                      # Check SUPPORT role.
    is_self                         # Accessing own resource.
    client_has_salesman             # Client has salesman.
    is_client_associated_salesman   # User is Client associated salesman.
    contract_has_salesman           # Contract's Client has salesman.
    is_contract_associated_salesman # User is the salesman linked to the
                                    # contract through client.
    contract_is_signed              # Contract's Client is signed.
    event_has_support               # Event has support.
    is_event_associated_support     # User is Event associated support.
    is_event_associated_salesman    # User is the salesman linked to the
                                    # event through contract & client.

References
    Tamás answer found at
    https://stackoverflow.com/questions/9184632/pointfree-function-combination-in-python
"""
from functools import update_wrapper

from ee_crm.domain.model import Role
from ee_crm.exceptions import BadToken, AuthorizationDenied
from ee_crm.services.auth.jwt_handler import verify_token


class P:
    """This class implements a way to combine multiple functions to
    form complex predicates, which value is returned when the class is
    called.

    It creates a function that will combine the given functions using
    the bitwise operators & (and), | (or) and ~ (not). At the minimal
    level a function will be wrapped by P and the predicate of P will
    be combined.

    Attributes
        pred (callable): The predicate that will be called.
        func_name (str): The name of the function, used for debugging.

    References
        Tamás answer found at
        https://stackoverflow.com/questions/9184632/pointfree-function-combination-in-python
    """
    def __init__(self, func, label=None):
        self.pred = func
        self.func_name = label or func.__name__

    def __call__(self, ctx):
        """Evaluate the predicate with a given context.

        Args
            ctx (dict): Context information given to the predicate.

        Returns
            bool: The result of the predicate evaluation.
        """
        return self.pred(ctx)

    def __and__(self, other):
        """Return a predicate representing 'self and other'.

        Returns
            P: A predicate.
        """
        def func(ctx):
            return self(ctx) and other(ctx)
        return P(func, label=f'({self.func_name} and {other.func_name})')

    def __or__(self, other):
        """Return a predicate representing 'self or other'.

        Returns
            P: A predicate.
        """
        def func(ctx):
            return self(ctx) or other(ctx)
        return P(func, label=f'({self.func_name} or {other.func_name})')

    def __invert__(self):
        """Return a predicate representing 'not self'.

        Returns
            P: A predicate.
        """
        def func(ctx):
            return not self(ctx)
        return P(func, label=f'not {self.func_name}')

    def __repr__(self):
        """Return a string representation of the predicate."""
        return self.func_name


def predicate(func):
    """A decorator that wraps a function in a class P to allows the
    creation of complex predicates.

    Args
        func (callable): The function to be wrapped, it should return a
            bool.
    """
    result = P(func)
    update_wrapper(result, func)
    return result


def is_authenticated():
    """This function is always a part of any permission.

    Returns
        bool: True if authenticated, False otherwise.

    Exceptions
        AuthorizationDenied: If the user is not authenticated.
    """
    try:
        return verify_token()
    except BadToken as e:
        err = AuthorizationDenied('Authentication invalid')
        err.tips = e.tips
        raise err


@predicate
def is_management(ctx):
    """This predicate checks if the user role is management (3).

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is management, False otherwise.
    """
    return ctx['auth']['role'] == Role.MANAGEMENT


@predicate
def is_sales(ctx):
    """This predicate checks if the user role is sales (4).

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is sales, False otherwise.
    """
    return ctx['auth']['role'] == Role.SALES


@predicate
def is_support(ctx):
    """This predicate checks if the user role is support (5).

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is support, False otherwise.
    """
    return ctx['auth']['role'] == Role.SUPPORT


@predicate
def is_self(ctx):
    """This predicate checks if the user is trying to access itself.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is accessing itself, False otherwise.
    """
    return ctx.get('pk', None) == ctx['auth']['c_id']


@predicate
def client_has_salesman(ctx):
    """This predicate checks if the accessed client has an associated
    salesman.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the client resource has a salesman, False
            otherwise.
    """
    client_id = ctx.get('pk', None)
    service = ctx['perm_service']
    salesman_id = service.get_client_associated_salesman(client_id)
    return salesman_id is not None


@predicate
def is_client_associated_salesman(ctx):
    """This predicate checks if the user is also the salesman of the
    accessed client resource.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is also the salesman of the client, False
            otherwise.
    """
    client_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    salesman_id = service.get_client_associated_salesman(client_id)
    return salesman_id == logged_user_id


@predicate
def contract_has_salesman(ctx):
    """This predicate checks if client associated with the accessed
    contract resource has a salesman.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the client of the contract has a salesman, False
            otherwise.
    """
    contract_id = ctx.get('pk', None)
    service = ctx['perm_service']
    salesman_id = service.get_contract_associated_salesman(contract_id)
    return salesman_id is not None


@predicate
def is_contract_associated_salesman(ctx):
    """This predicate checks if client associated with the accessed
    contract resource has a salesman.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the client of the contract has a salesman, False
            otherwise.
    """
    contract_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    salesman_id = service.get_contract_associated_salesman(contract_id)
    return salesman_id == logged_user_id


@predicate
def contract_is_signed(ctx):
    """This predicate checks if the contract is signed.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the contract is signed, False otherwise.
    """
    contract_id = ctx.get('pk', None)
    service = ctx['perm_service']
    signed = service.get_contract_signed(contract_id)
    return signed is True


@predicate
def event_has_support(ctx):
    """This predicate checks if the event has a support.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the event has support, False otherwise.
    """
    event_id = ctx.get('pk', None)
    service = ctx['perm_service']
    supporter_id = service.get_event_support(event_id)
    return supporter_id is not None


@predicate
def is_event_associated_support(ctx):
    """This predicate checks if user is the support of the event.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is the event associated support, False
            otherwise.
    """
    event_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    supporter_id = service.get_event_support(event_id)
    return supporter_id == logged_user_id


@predicate
def is_event_associated_salesman(ctx):
    """This predicate checks if the user is also the salesman of the
    client, associated to the contract associated to the event.

    Args
        ctx (dict): Context information given to the predicate.

    Returns
        bool: True if the user is the salesman associated to the event
        through contract and client, False otherwise.
    """
    event_id = ctx.get('pk', None)
    logged_user_id = ctx['auth']['c_id']
    service = ctx['perm_service']
    salesman_id = service.get_event_associated_salesman(event_id)
    return salesman_id == logged_user_id
