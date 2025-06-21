import pytest

from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.auth import predicate
from ee_crm.controllers.auth.predicate import is_authenticated, is_self, \
    is_management, is_sales, is_support
from ee_crm.exceptions import AuthorizationDenied
from ee_crm.services.auth.jwt_handler import BadToken


@pytest.fixture
def mock_user_management(mocker):
    payload = {
        'sub': 'user_01',
        'c_id': 1,
        'role': 3,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }
    mocker.patch("ee_crm.controllers.auth.permission.is_authenticated",
                 return_value=payload)


@pytest.fixture
def mock_user_sales(mocker):
    payload = {
        'sub': 'user_02',
        'c_id': 2,
        'role': 4,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }
    mocker.patch("ee_crm.controllers.auth.permission.is_authenticated",
                 return_value=payload)


@pytest.fixture
def mock_user_support(mocker):
    payload = {
        'sub': 'user_03',
        'c_id': 3,
        'role': 5,
        'name': 'Charmion Garthland',
        'iat': 1748116252,
        'exp': 1748116342
    }
    mocker.patch("ee_crm.controllers.auth.permission.is_authenticated",
                 return_value=payload)


@pytest.fixture(autouse=True)
def mock_perms(mocker):
    rbac = {
        "BASE": {"mock:base"},
        "COLLABORATOR": {"mock:collaborator"},
        "MANAGEMENT": {"mock:management"},
        "SALES": {"mock:sales"},
        "SUPPORT": {"mock:support"},
    }
    perms = {
        "DEACTIVATED": rbac["BASE"],
        "ADMIN": rbac["BASE"],
        "MANAGEMENT": set().union(rbac["BASE"],
                                  rbac["COLLABORATOR"],
                                  rbac["MANAGEMENT"]),
        "SALES": set().union(rbac["BASE"],
                             rbac["COLLABORATOR"],
                             rbac["SALES"]),
        "SUPPORT": set().union(rbac["BASE"],
                               rbac["COLLABORATOR"],
                               rbac["SUPPORT"]),
    }
    mocker.patch('ee_crm.controllers.auth.permission.PERMS', perms)


@pytest.mark.parametrize(
    'payload',
    [
        {'sub': 'user_01',
         'c_id': 1,
         'role': 3,
         'name': 'Charmion Garthland',
         'iat': 1748116252,
         'exp': 1748116342
         },
        {'sub': 'user_01',
         'c_id': 2,
         'role': 4,
         'name': 'Charmion Garthland',
         'iat': 1748116252,
         'exp': 1748116342
         },
        {'sub': 'user_01',
         'c_id': 3,
         'role': 5,
         'name': 'Charmion Garthland',
         'iat': 1748116252,
         'exp': 1748116342
         }
    ]
)
def test_is_authenticated_success(mocker, payload):
    mocker.patch.object(predicate, 'verify_token',
                        return_value=payload)
    assert is_authenticated()['c_id'] == payload['c_id']


def test_is_authenticated_failure(mocker):
    verify_token = mocker.patch.object(predicate, 'verify_token',
                                       return_value=None)
    verify_token.side_effect = BadToken("No access token")
    with pytest.raises(AuthorizationDenied, match="Authentication invalid"):
        is_authenticated()


def test_permission_with_bad_authenticated(mocker):
    verify_token = mocker.patch.object(predicate, 'verify_token',
                                       return_value=None)
    verify_token.side_effect = BadToken("No access token")

    @permission("mock:base")
    def test_func():
        pass

    with pytest.raises(AuthorizationDenied, match="Authentication invalid"):
        test_func()


def test_permission_with_kwargs_get_payload(mock_user_management):
    @permission("mock:base")
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func()


def test_permission_without_kwargs_dont_get_payload(mock_user_management):
    @permission("mock:base")
    def test_func():
        pass

    test_func()


def test_rbac_permission_support(mock_user_support):
    @permission("mock:support")
    def test_func():
        pass

    test_func()


def test_rbac_permission_sales(mock_user_sales):
    @permission("mock:sales")
    def test_func():
        pass

    test_func()


def test_rbac_permission_management(mock_user_management):
    @permission("mock:management")
    def test_func():
        pass

    test_func()


def test_rbac_permission_support_get_collaborator_right(mock_user_support):
    @permission("mock:collaborator")
    def test_func():
        pass

    test_func()


def test_rbac_permission_support_dont_get_sales_right(mock_user_support):
    @permission("mock:sales")
    def test_func():
        pass

    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error \(RBAC\) "
                             r"in \('mock:sales',\)."):
        test_func()


def test_rbac_permission_can_use_multiple_args(mock_user_support):
    @permission("mock:sales", "mock:management", "invented:tag",
                "mock:support")
    def test_func():
        pass

    test_func()


def test_rbac_permission_right_and_abac(mock_user_management):
    @permission("mock:management", "invented:tag",
                abac=(is_management & ~is_support))
    def test_func():
        pass

    test_func()


def test_permission_with_kwargs_kw_auth_false_dont_get_payload(
        mock_user_management):
    @permission("mock:base", kw_auth=False)
    def test_func(**kwargs):
        with pytest.raises(KeyError):
            assert kwargs['auth']['c_id'] == 1
            assert kwargs['auth']['role'] == 3

    test_func()


def test_permission_is_manager(mock_user_management):
    @permission("mock:base", abac=is_management)
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func(keyword='keyword')


def test_permission_is_manager_or_is_sales(mock_user_management):
    @permission("mock:base", abac=(is_management | is_sales))
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 1
        assert kwargs['auth']['role'] == 3

    test_func(keyword='keyword')


def test_permission_is_support_or_is_sales_or_is_manager(mock_user_support):
    @permission("mock:base", abac=((is_management & is_sales) | is_support))
    def test_func(**kwargs):
        assert kwargs['auth']['c_id'] == 3
        assert kwargs['auth']['role'] == 5

    test_func(keyword='keyword')


def test_permission_is_manager_and_is_sales_raise_error(mock_user_management):
    @permission("mock:base", abac=(is_management & is_sales))
    def test_func(**kwargs):
        pass

    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error \(ABAC\) "
                             r"in \(is_management and is_sales\)"):
        test_func(keyword='keyword')


def test_permission_is_self_1_success(mock_user_management):
    @permission("mock:base", abac=is_self)
    def test_func(pk, **kwargs):
        pass

    pk_id = 1
    test_func(pk_id, keyword='keyword')


def test_permission_is_self_2_success(mock_user_sales):
    @permission("mock:base", abac=is_self)
    def test_func(pk, **kwargs):
        pass

    pk_id = 2
    test_func(pk_id, keyword='keyword')


def test_permission_is_self_failure_not_self(mock_user_sales):
    @permission("mock:base", abac=is_self)
    def test_func(pk, **kwargs):
        pass

    pk_id = 3
    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error \(ABAC\) in is_self"):
        test_func(pk_id, keyword='keyword')


def test_permission_is_self_or_management_success(mock_user_management):
    @permission("mock:base", abac=(is_self | is_management))
    def test_func(pk, **kwargs):
        pass

    pk_id = 3
    test_func(pk_id, keyword='keyword')


def test_permission_is_self_failure_bad_signature(mock_user_support):
    # reminder, for [is_self] to work, pk must be a part of the signature
    # of the func
    @permission("mock:base", abac=is_self)
    def test_func(not_pk, **kwargs):
        pass

    pk_id = 3

    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error \(ABAC\) in is_self"):
        test_func(pk_id, keyword='keyword')


def test_permission_can_be_inverted(mock_user_sales):
    @permission("mock:base", abac=~is_management & ~is_support)
    def test_func(**kwargs):
        pass

    test_func(keyword='keyword')


def test_permission_is_management_can_be_inverted(mock_user_management):
    @permission("mock:base", abac=~is_management)
    def test_func(**kwargs):
        pass

    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error \(ABAC\) in "
                             r"not is_management"):
        test_func(keyword='keyword')
