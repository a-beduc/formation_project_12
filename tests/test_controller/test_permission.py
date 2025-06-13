import pytest

from ee_crm.controllers import permission as p
from ee_crm.services.auth.jwt_handler import BadToken
from ee_crm.controllers.permission import (
    is_client_associated_salesman,
    contract_has_salesman,
    is_contract_associated_salesman,
    contract_is_signed,
    event_has_support,
    is_event_associated_support,
    is_event_associated_salesman
)


def valid_management_payload():
    return {
        'sub': 'user_01',
        'c_id': 1,
        'role': 3,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }


def valid_sales_payload():
    return {
        'sub': 'user_02',
        'c_id': 2,
        'role': 4,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }


def valid_support_payload():
    return {
        'sub': 'user_03',
        'c_id': 3,
        'role': 5,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }


@pytest.mark.parametrize(
    'payload',
    [
        valid_management_payload(),
        valid_sales_payload(),
        valid_support_payload(),
    ]
)
def test_is_authenticated_success(mocker, payload):
    mocker.patch.object(p, 'verify_token',
                        return_value=payload)
    assert p.is_authenticated()['c_id'] == payload['c_id']


def test_is_authenticated_failure(mocker):
    verify_token = mocker.patch.object(p, 'verify_token',
                                       return_value=None)
    verify_token.side_effect = BadToken("No access token")
    with pytest.raises(p.AuthorizationDenied, match="Authentication invalid"):
        p.is_authenticated()


def test_permission_with_bad_authenticated(mocker):
    verify_token = mocker.patch.object(p, 'verify_token',
                                       return_value=None)
    verify_token.side_effect = BadToken("No access token")

    @p.permission
    def test_func():
        pass

    with pytest.raises(p.AuthorizationDenied, match="Authentication invalid"):
        test_func()


def test_permission_with_kwargs_get_payload(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func()


def test_permission_without_kwargs_dont_get_payload(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission
    def test_func():
        pass

    test_func()


def test_permission_with_kwargs_kw_auth_false_dont_get_payload(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(kw_auth=False)
    def test_func(**kwargs):
        with pytest.raises(KeyError):
            assert kwargs['auth']['c_id'] == 1
            assert kwargs['auth']['role'] == 3

    test_func()


def test_permission_is_manager(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=p.is_management)
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func(keyword='keyword')


def test_permission_is_manager_or_is_sales(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=(p.is_management | p.is_sales))
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func(keyword='keyword')


def test_permission_is_support_or_is_sales_or_is_manager(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_support_payload())

    @p.permission(requirements=((p.is_management & p.is_sales) | p.is_support))
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 3
        assert kwargs['auth']['role'] == 5

    test_func(keyword='keyword')


def test_permission_is_manager_and_is_sales_raise_error(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=(p.is_management & p.is_sales))
    def test_func(**kwargs):
        pass

    with pytest.raises(p.AuthorizationDenied,
                       match=r"Permission error in "
                             r"\(is_management and is_sales\)"):
        test_func(keyword='keyword')


def test_permission_is_self_1_success(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=p.is_self)
    def test_func(pk, **kwargs):
        pass

    pk_id = valid_management_payload()['c_id']
    test_func(pk_id, keyword='keyword')


def test_permission_is_self_2_success(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_sales_payload())

    @p.permission(requirements=p.is_self)
    def test_func(pk, **kwargs):
        pass

    pk_id = valid_sales_payload()['c_id']
    test_func(pk_id, keyword='keyword')


def test_permission_is_self_failure_not_self(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_sales_payload())

    @p.permission(requirements=p.is_self)
    def test_func(pk, **kwargs):
        pass

    pk_id = valid_support_payload()['c_id']

    with pytest.raises(p.AuthorizationDenied,
                       match="Permission error in is_self"):
        test_func(pk_id, keyword='keyword')


def test_permission_is_self_or_management_success(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=(p.is_self | p.is_management))
    def test_func(pk, **kwargs):
        pass

    pk_id = valid_support_payload()['c_id']
    test_func(pk_id, keyword='keyword')


def test_permission_is_self_failure_bad_signature(mocker):
    # reminder, for [is_self] to work, pk must be a part of the signature
    # of the func
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_support_payload())

    @p.permission(requirements=p.is_self)
    def test_func(not_pk, **kwargs):
        pass

    pk_id = valid_support_payload()['c_id']

    with pytest.raises(p.AuthorizationDenied,
                       match="Permission error in is_self"):
        test_func(pk_id, keyword='keyword')


def test_permission_can_be_inverted(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_sales_payload())

    @p.permission(requirements=~p.is_management & ~p.is_support)
    def test_func(**kwargs):
        pass

    test_func(keyword='keyword')


def test_permission_is_management_can_be_inverted(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=~p.is_management)
    def test_func(**kwargs):
        pass

    with pytest.raises(p.AuthorizationDenied,
                       match=r"Permission error in not is_management"):
        test_func(keyword='keyword')
