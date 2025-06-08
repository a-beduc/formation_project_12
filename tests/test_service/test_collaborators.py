import pytest

from ee_crm.services.app.collaborators import (CollaboratorService,
                                               CollaboratorServiceError)
from ee_crm.services.dto import CollaboratorDTO
from ee_crm.domain.model import (AuthUserError, AuthUser, Collaborator, Role,
                                 CollaboratorError)
from ee_crm.domain.validators import AuthUserValidatorError

from tests.test_service.conftest import FakeRepository


@pytest.fixture
def init_uow(uow):
    user_a = AuthUser.builder("user_a", "Password1")
    user_b = AuthUser.builder("user_b", "Password2")
    user_c = AuthUser.builder("user_c", "Password3")
    user_d = AuthUser.builder("user_d", "Password4")
    user_e = AuthUser.builder("user_e", "Password5")
    uow.users = FakeRepository(init=(user_a, user_b, user_c, user_d, user_e))

    coll_a = Collaborator(first_name="fn_a", last_name="ln_a",
                          _role_id=Role.MANAGEMENT, _user_id=1)
    coll_b = Collaborator(first_name="fn_b", last_name="ln_b",
                          _role_id=Role.SALES, _user_id=2)
    coll_c = Collaborator(first_name="fn_c", last_name="ln_c",
                          _role_id=Role.SALES, _user_id=3)
    coll_d = Collaborator(first_name="fn_d", last_name="ln_d",
                          _role_id=Role.SUPPORT, _user_id=4)
    coll_e = Collaborator(first_name="fn_e", last_name="ln_e",
                          _role_id=Role.SUPPORT, _user_id=5)
    uow.collaborators = FakeRepository(init=(coll_a, coll_b, coll_c, coll_d,
                                             coll_e))

    return uow


class TestCollaboratorCreation:

    def test_user_creation_success(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        service = CollaboratorService(init_uow)
        service.create("user_test", "Password1", **data)
        assert init_uow.commited is True

        collaborator = init_uow.collaborators.get(6)
        assert collaborator.id == 6
        assert collaborator.last_name == "Bobby"
        assert collaborator.first_name == "Robby"
        assert collaborator.email == "test@test.c"
        assert collaborator.phone_number == "0000000001"
        assert collaborator.role == Role.DEACTIVATED
        assert collaborator.user_id == 6

    def test_user_creation_password_error(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        service = CollaboratorService(init_uow)

        with pytest.raises(AuthUserValidatorError,
                           match="password too weak, need at least 8 char, "
                                 "1 number, 1 upper, 1 lower"):
            service.create("user_test", "pwd", **data)

    def test_user_creation_empty_username(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(init_uow)

        with pytest.raises(AuthUserValidatorError, match="Username too short"):
            collaborator_service.create("", plain_password="Password1", **data)

    def test_user_creation_username_taken(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(init_uow)

        with pytest.raises(CollaboratorServiceError, match="username taken"):
            collaborator_service.create("user_a", "Password1", **data)

    def test_user_creation_uow_failure(self, mocker, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }

        def uow_error():
            raise RuntimeError("db crash")

        mocker.patch.object(init_uow, "commit", uow_error)
        collaborator_service = CollaboratorService(init_uow)
        spy_uow_rollback = mocker.spy(init_uow, "rollback")

        with pytest.raises(RuntimeError, match="db crash"):
            collaborator_service.create("user_test", "Password1", **data)

        assert spy_uow_rollback.call_count == 1


class TestCollaboratorCRUD:
    def test_get_collaborator_from_user_id(self, init_uow):
        service = CollaboratorService(init_uow)

        dto_coll_a = CollaboratorDTO.from_domain(init_uow.collaborators.get(1))
        dto_coll_b = CollaboratorDTO.from_domain(init_uow.collaborators.get(2))

        assert service.filter(user_id=1) == [dto_coll_a]
        assert service.filter(user_id=2) == [dto_coll_b]
        assert service.filter(user_id=8) == []

    def test_get_collaborator(self, init_uow):
        service = CollaboratorService(init_uow)

        dto_coll_a = CollaboratorDTO.from_domain(init_uow.collaborators.get(1))

        assert service.retrieve(1) == dto_coll_a

    def test_get_all_salesmen(self, init_uow):

        service = CollaboratorService(init_uow)

        dto_coll_b = CollaboratorDTO.from_domain(init_uow.collaborators.get(2))
        dto_coll_c = CollaboratorDTO.from_domain(init_uow.collaborators.get(3))

        list_of_salesmen = service.filter(role=4)
        assert list_of_salesmen == [dto_coll_b, dto_coll_c]

    def test_delete_collaborator(self, init_uow):
        service = CollaboratorService(init_uow)

        assert service.retrieve(1).first_name == "fn_a"

        service.remove(1)
        assert init_uow.commited is True

        with pytest.raises(CollaboratorServiceError,
                           match="Collaborator not found"):
            service.retrieve(1)

    def test_update_collaborator(self, init_uow):
        service = CollaboratorService(init_uow)
        update_input = {"user_id": 10, "last_name": "new_last_name"}
        service.modify(1, **update_input)

        assert init_uow.commited is True
        assert service.retrieve(1).last_name == "new_last_name"
        # user_id is a protected field, no update authorized.
        assert service.retrieve(1).user_id == 1

    def test_assign_role_success(self, init_uow):
        service = CollaboratorService(init_uow)
        user_1_dto_before = service.retrieve(1)
        assert user_1_dto_before.role == Role.MANAGEMENT

        service.assign_role(1, role="ADMIN")
        user_1_dto_after = service.retrieve(1)
        assert user_1_dto_after.role == Role.ADMIN

    def test_assign_role_fail(self, init_uow):
        service = CollaboratorService(init_uow)
        with pytest.raises(CollaboratorError,
                           match="Role must be an instance of RoleType"):
            service.assign_role(1, role="UNKNOWN")
