"""Unit tests for ee_crm.services.auth.permissions

Each test confirms that the service returns 'None' when the requested
resource is missing.

Fixtures
    fake_repo
        fake repository class, when called create an instance of a
        FakeRepository that expose fake repositories for resources.
"""
from ee_crm.services.auth.permissions import PermissionService


def test_get_client_associated_salesman_fail(fake_uow):
    service = PermissionService(fake_uow)
    assert service.get_client_associated_salesman(12) is None


def test_get_contract_associated_salesman_fail(fake_uow):
    service = PermissionService(fake_uow)
    assert service.get_contract_associated_salesman(12) is None


def test_contract_signed_fail(fake_uow):
    service = PermissionService(fake_uow)
    assert service.get_contract_signed(12) is None


def test_get_event_support_fail(fake_uow):
    service = PermissionService(fake_uow)
    assert service.get_event_support(12) is None


def test_get_event_associated_salesman_fail(fake_uow):
    service = PermissionService(fake_uow)
    assert service.get_event_associated_salesman(12) is None
