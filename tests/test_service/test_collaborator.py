import pytest

from services.app.collaborator import (CollaboratorService,
                                       CollaboratorServiceError)
from services.dto import CollaboratorDTO, AuthUserDTO
from domain.model import AuthUserError, AuthUser, Collaborator
from tests.test_service.conftest import (FakeUserRepository,
                                         FakeCollaboratorRepository)


class TestCollaboratorCreation:
    def test_user_creation_success(self, uow):
        expected = (
            AuthUserDTO(
                1, "user_test"),
            CollaboratorDTO(
                1, "Bobby", "Robby", "test@test.c", "0000000001", 1, 1),
        )
        data = {
            "username": "user_test",
            "plain_password": "Password1",
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(uow)
        user, collaborator = (collaborator_service.
                              create_collaborator_with_user(**data))
        assert expected[0] == user
        assert expected[1] == collaborator

    def test_user_creation_password_error(self, uow):
        data = {
            "username": "user_test",
            "plain_password": "password",
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(uow)

        with pytest.raises(AuthUserError,
                           match="password too weak, need 8 char, 1 number, "
                                 "1 upper, 1 lower"):
            collaborator_service.create_collaborator_with_user(**data)

    def test_user_creation_missing_username(self, uow):
        data = {
            "username": "",
            "plain_password": "Password1",
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(uow)

        with pytest.raises(AuthUserError, match="username too short"):
            collaborator_service.create_collaborator_with_user(**data)

    def test_user_creation_username_taken(self, uow):
        user = AuthUser(username="user_test", password="<PASSWORD>")
        uow.users = FakeUserRepository(init=(user,))
        data = {
            "username": "user_test",
            "plain_password": "Password1",
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }
        collaborator_service = CollaboratorService(uow)

        with pytest.raises(AuthUserError, match="username taken"):
            collaborator_service.create_collaborator_with_user(**data)

    def test_user_creation_uow_failure(self, mocker, uow):
        data = {
            "username": "user_test",
            "plain_password": "Password1",
            "last_name": "Bobby",
            "first_name": "Robby",
            "email": "test@test.c",
            "phone_number": "0000000001"
        }

        def uow_error():
            raise RuntimeError("db crash")

        mocker.patch.object(uow, "commit", uow_error)
        collaborator_service = CollaboratorService(uow)
        spy_uow_rollback = mocker.spy(uow, "rollback")

        with pytest.raises(RuntimeError, match="db crash"):
            collaborator_service.create_collaborator_with_user(**data)

        assert spy_uow_rollback.call_count == 1


class TestCollaboratorCRUD:
    @staticmethod
    def init_repos(init_uow):
        user_a = AuthUser(username="user_a", password="password_a")
        user_b = AuthUser(username="user_b", password="password_b")
        user_c = AuthUser(username="user_c", password="password_c")
        user_d = AuthUser(username="user_d", password="password_d")
        user_e = AuthUser(username="user_e", password="password_e")
        init_uow.users = FakeUserRepository(
            init=(user_a, user_b, user_c, user_d, user_e))

        coll_a = Collaborator(first_name="fn_a", last_name="ln_a", role_id=4,
                              user_id=1)
        coll_b = Collaborator(first_name="fn_b", last_name="ln_b", role_id=4,
                              user_id=2)
        coll_c = Collaborator(first_name="fn_c", last_name="ln_c", role_id=3,
                              user_id=3)
        coll_d = Collaborator(first_name="fn_d", last_name="ln_d", role_id=5,
                              user_id=4)
        coll_e = Collaborator(first_name="fn_e", last_name="ln_e", role_id=5,
                              user_id=5)
        init_uow.collaborators = FakeCollaboratorRepository(
            init=(coll_a, coll_b, coll_c, coll_d, coll_e))
        return init_uow

    def test_get_collaborator_from_user_id(self, uow):
        uow = self.init_repos(uow)
        service = CollaboratorService(uow)

        dto_coll_a = CollaboratorDTO.from_domain(uow.collaborators.get(1))
        dto_coll_b = CollaboratorDTO.from_domain(uow.collaborators.get(2))

        assert service.get_collaborator_from_user_id(1) == dto_coll_a
        assert service.get_collaborator_from_user_id(2) == dto_coll_b
        with pytest.raises(CollaboratorServiceError,
                           match="Collaborator not found"):
            service.get_collaborator_from_user_id(8)

    def test_get_collaborator(self, uow):
        uow = self.init_repos(uow)
        service = CollaboratorService(uow)

        dto_coll_a = CollaboratorDTO.from_domain(uow.collaborators.get(1))

        assert service.get_collaborator_by_id(1) == dto_coll_a

    def test_get_all_salesmen(self, uow):
        uow = self.init_repos(uow)

        service = CollaboratorService(uow)

        dto_coll_a = CollaboratorDTO.from_domain(uow.collaborators.get(1))
        dto_coll_b = CollaboratorDTO.from_domain(uow.collaborators.get(2))

        list_of_salesmen = service.get_list_of_collaborators(
            filter_by_role_id=4)
        assert list_of_salesmen == [dto_coll_a, dto_coll_b]

    def test_delete_collaborator(self, uow):
        uow = self.init_repos(uow)
        service = CollaboratorService(uow)

        assert service.get_collaborator_by_id(1).first_name == "fn_a"

        service.delete_collaborator(1)

        with pytest.raises(CollaboratorServiceError,
                           match="Collaborator not found"):
            service.get_collaborator_by_id(1)

    def test_update_collaborator(self, uow):
        uow = self.init_repos(uow)
        service = CollaboratorService(uow)
        update_input = {"user_id": 10, "last_name": "new_last_name"}
        service.update_collaborator(1, **update_input)

        assert service.get_collaborator_by_id(1).last_name == "new_last_name"
        assert service.get_collaborator_by_id(1).user_id == 1
