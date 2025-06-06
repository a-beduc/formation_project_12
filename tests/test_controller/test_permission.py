import pytest

from ee_crm.controllers import permission as p


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
        'sub': 'user_01',
        'c_id': 1,
        'role': 4,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }


def valid_support_payload():
    return {
        'sub': 'user_01',
        'c_id': 1,
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
    mocker.patch.object(p, 'check_token',
                        return_value=payload)
    assert p.is_authenticated()['c_id'] == 1


def test_is_authenticated_failure(mocker):
    mocker.patch.object(p, 'check_token',
                        return_value=None)
    with pytest.raises(PermissionError, match="Authentication invalid"):
        p.is_authenticated()


def test_permission_with_bad_authenticated(mocker):
    mocker.patch.object(p, 'check_token',
                        return_value=None)

    @p.permission
    def test_func():
        pass

    with pytest.raises(PermissionError, match="Authentication invalid"):
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

    @p.permission(requirements=[(p.is_management,)])
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func(keyword='keyword')


def test_permission_is_manager_or_is_sales(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=[(p.is_management, p.is_sales)])
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func(keyword='keyword')


def test_permission_is_manager_and_is_sales_raise_error(mocker):
    mocker.patch.object(p, "is_authenticated",
                        return_value=valid_management_payload())

    @p.permission(requirements=[(p.is_management,), (p.is_sales,)])
    def test_func(**kwargs):
        pass

    with pytest.raises(PermissionError):
        test_func(keyword='keyword')
