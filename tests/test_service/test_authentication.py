import pytest

from ee_crm.domain.model import AuthUser, Collaborator, AuthUserDomainError
from ee_crm.services.auth.authentication import (
    AuthenticationService,
    AuthenticationError)


class TestAuthenticate:
    def test_authenticate_success(self, mocker, uow, fake_repo):
        user = AuthUser(_username="user_b",
                        _password="Password1")
        uow.users = fake_repo(init=(user,))
        collaborator = Collaborator(_user_id=1,
                                    last_name="Ross",
                                    first_name="Bobby")
        uow.collaborators = fake_repo(init=(collaborator,))

        service = AuthenticationService(uow)
        expected_payload = {
            "sub": "user_b",
            "c_id": 1,
            "role": 1,
            "name": "Bobby Ross",
        }
        mocker.patch.object(uow.users, "filter_one", return_value=user)
        mocker.patch.object(user, "verify_password")
        mocker.patch.object(uow.collaborators,
                            "filter_one",
                            return_value=collaborator)

        spy_filter_by_username = mocker.spy(uow.users, "filter_one")
        spy_verify = mocker.spy(user, "verify_password")
        spy_filter_by_user_id = mocker.spy(uow.collaborators, "filter_one")

        assert service.authenticate("user_b", "Password1") == expected_payload

        assert spy_filter_by_username.call_count == 1
        assert spy_verify.call_count == 1
        assert spy_filter_by_user_id.call_count == 1

    def test_authenticate_fail_wrong_username(self, uow):
        with pytest.raises(AuthenticationError,
                           match='No user found with username : "not_bob"'):
            service = AuthenticationService(uow)
            service.authenticate("not_bob", "pwd")

    def test_authenticate_fail_wrong_password(self, uow, mocker, fake_repo):
        user = AuthUser(_username="user_b",
                        _password="Password1")
        uow.users = fake_repo(init=(user,))
        collaborator = Collaborator(_user_id=1,
                                    last_name="Ross",
                                    first_name="Bobby")
        uow.collaborators = fake_repo(init=(collaborator,))

        service = AuthenticationService(uow)

        mocker.patch.object(uow.users, "filter_one", return_value=user)
        mock_vp = mocker.patch.object(user, "verify_password")
        mock_vp.side_effect = AuthUserError("Password mismatch")

        with pytest.raises(AuthUserError, match="Password mismatch"):
            service.authenticate("user_b", "not_pwd")
