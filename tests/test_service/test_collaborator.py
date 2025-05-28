import pytest

from services.app.collaborators import (CollaboratorService,
                                        CollaboratorServiceError)
from services.dto import CollaboratorDTO, AuthUserDTO
from domain.model import AuthUserError, AuthUser, Collaborator
from tests.test_service.conftest import FakeRepository


@pytest.fixture
def init_uow(uow):
    user_a = AuthUser.build_user("user_a", "Password1")
    user_b = AuthUser.build_user("user_b", "Password2")
    user_c = AuthUser.build_user("user_c", "Password3")
    user_d = AuthUser.build_user("user_d", "Password4")
    user_e = AuthUser.build_user("user_e", "Password5")
    uow.users = FakeRepository(init=(user_a, user_b, user_c, user_d, user_e))

    coll_a = Collaborator(first_name="fn_a", last_name="ln_a", role_id=3,
                          user_id=1)
    coll_b = Collaborator(first_name="fn_b", last_name="ln_b", role_id=4,
                          user_id=2)
    coll_c = Collaborator(first_name="fn_c", last_name="ln_c", role_id=4,
                          user_id=3)
    coll_d = Collaborator(first_name="fn_d", last_name="ln_d", role_id=5,
                          user_id=4)
    coll_e = Collaborator(first_name="fn_e", last_name="ln_e", role_id=5,
                          user_id=5)
    uow.collaborators = FakeRepository(init=(coll_a, coll_b, coll_c, coll_d,
                                             coll_e))

    return uow


class TestCollaboratorCreation:

    def test_user_creation_success(self, init_uow):
        expected = (
            AuthUserDTO(id=6, username="user_test"),
            CollaboratorDTO(id=6, last_name="Bobby", first_name="Robby",
                            user_id=6, role_id=1, email="test@test.c", phone_number="0000000001")
        )
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        service = CollaboratorService(init_uow)
        user, collaborator = service.create("user_test", "Password1", **data)
        assert expected[0] == user
        assert expected[1] == collaborator

    def test_user_creation_password_error(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(init_uow)

        with pytest.raises(AuthUserError,
                           match="password too weak, need 8 char, 1 number, "
                                 "1 upper, 1 lower"):
            collaborator_service.create("user_test", "pwd", **data)

    def test_user_creation_empty_username(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(init_uow)

        with pytest.raises(AuthUserError, match="username too short"):
            collaborator_service.create("", plain_password="Password1", **data)

    def test_user_creation_username_taken(self, init_uow):
        data = {
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(init_uow)

        with pytest.raises(AuthUserError, match="username taken"):
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

        list_of_salesmen = service.filter(role_id=4)
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
