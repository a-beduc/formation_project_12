import pytest

from ee_crm.controllers.app.collaborator import CollaboratorManager
from ee_crm.services.dto import CollaboratorDTO
from ee_crm.domain.model import Role, CollaboratorError
from ee_crm.controllers.permission import AuthorizationDenied


@pytest.fixture
def collaborators_dto():
    coll_a = CollaboratorDTO(
        id=1,
        last_name="ln_a",
        first_name="fn_a",
        email="a@email",
        phone_number="0000000001",
        role=3,
        user_id=1
    )
    coll_b = CollaboratorDTO(
        id=2,
        last_name="ln_b",
        first_name="fn_b",
        email="b@email",
        phone_number="0000000002",
        role=4,
        user_id=2
    )
    coll_c = CollaboratorDTO(
        id=3,
        last_name="ln_c",
        first_name="fn_c",
        email="c@email",
        phone_number="0000000003",
        role=5,
        user_id=3
    )
    return coll_a, coll_b, coll_c


def test_read_by_pk(fake_service, collaborators_dto, bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    fake_service.retrieve.return_value = collaborators_dto[0]
    pk = 1
    result = controller.read(pk=pk)

    fake_service.retrieve.assert_called_once_with(pk)
    assert result == collaborators_dto[0]


def test_read_all(fake_service, collaborators_dto, bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    fake_service.retrieve_all.return_value = collaborators_dto
    result = controller.read()

    fake_service.retrieve_all.assert_called_once_with(sort=None)
    assert result == collaborators_dto


def test_read_all_sort_by_reverse_id(fake_service, collaborators_dto,
                                     bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    fake_service.retrieve_all.return_value = collaborators_dto[::-1]
    sort = (("id", True),)
    result = controller.read(sort=sort)

    fake_service.retrieve_all.assert_called_once_with(sort=sort)
    assert result == collaborators_dto[::-1]


def test_read_filter_by_last_name(fake_service, collaborators_dto,
                                  bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    fake_service.filter.return_value = collaborators_dto[1]
    filters = {"last_name": "ln_b"}
    result = controller.read(filters=filters)

    fake_service.filter.assert_called_once_with(sort=None,
                                                **{"last_name": "ln_b"})
    assert result == collaborators_dto[1]


def test_validate_fields_remove_unwanted_key(fake_service):
    controller = CollaboratorManager(fake_service)
    input_data = {
        "first_name": "Bobby",
        "id": "13",
        "unknown": "unwanted data"
    }
    validated = controller._validate_fields(input_data)

    assert validated == {"first_name": "Bobby", "id": 13}


def test_read_filter_sort_by_unknown_field(fake_service, collaborators_dto,
                                           bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    filters = {"unknown": "unknown"}
    sort = (("unknown", True),)

    controller.read(filters=filters, sort=sort)

    fake_service.filter.assert_called_once_with(sort=(("unknown", True),),
                                                **{})


def test_create_collaborator_minimal_data(fake_service,
                                          bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    controller.create(username="Alfred", plain_password="Password1")
    fake_service.create.assert_called_once_with(
        "Alfred",
        "Password1",
        role=Role.DEACTIVATED
    )


def test_create_collaborator_with_support_role(fake_service,
                                               bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    controller.create(username="Banner", plain_password="Password1",
                      role="SUPPORT")
    fake_service.create.assert_called_once_with(
        "Banner",
        "Password1",
        role=Role.SUPPORT
    )


def test_create_collaborator_with_bad_role(fake_service,
                                           bypass_permission_manager):
    controller = CollaboratorManager(fake_service)

    with pytest.raises(CollaboratorError, match="Invalid role: BAD"):
        controller.create(username="Banner", plain_password="Password1",
                          role="BAD")


def test_create_permission_denied(fake_service, mocker):
    mocker.patch("ee_crm.controllers.permission.verify_token",
                 return_value={"sub": "user", "c_id": 13, "role": 5,
                               "name": "Bruce Banner"})
    controller = CollaboratorManager(fake_service)

    with pytest.raises(AuthorizationDenied,
                       match="Permission error in is_management"):
        controller.create(username="Banner", plain_password="Password1")


def test_change_collaborator_role(fake_service, bypass_permission_manager):
    controller = CollaboratorManager(fake_service)
    controller.change_collaborator_role(pk="5", role="MANAGEMENT")
    fake_service.assign_role.assert_called_once_with(5, Role.MANAGEMENT)
