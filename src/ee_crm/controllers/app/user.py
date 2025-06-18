from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.permission import permission, is_management
from ee_crm.controllers.utils import verify_positive_int, verify_string
from ee_crm.exceptions import UserManagerError
from ee_crm.services.app.collaborators import CollaboratorService
from ee_crm.services.app.users import UserService
from ee_crm.services.auth.authentication import AuthenticationService
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork


class UserManager(BaseManager):
    label = "User"
    _validate_types_map = {
        "id": int,
        "username": str,
    }
    _default_service = UserService(SqlAlchemyUnitOfWork())
    error_cls = UserManagerError

    @permission(requirements=is_management)
    def read(self, pk=None, filters=None, sort=None):
        return super().read(pk=pk, filters=filters, sort=sort)

    @permission
    def who_am_i(self, **kwargs):
        uow = SqlAlchemyUnitOfWork()
        c_id = kwargs['auth']['c_id']
        coll = CollaboratorService(uow).retrieve(c_id)[0]
        user = self.service.retrieve(coll.user_id)[0]
        return user, coll

    @permission
    def update_username(self, old_username, plain_password, new_username,
                        **kwargs):
        service_auth = AuthenticationService(SqlAlchemyUnitOfWork())
        payload = service_auth.authenticate(old_username, plain_password)

        if not payload['c_id'] == kwargs['auth']['c_id']:
            raise self.error_cls("You can't modify someone else username.")
        self.service.modify_username(str(old_username),
                                     str(plain_password),
                                     str(new_username))

    @permission
    def update_password(self, username, old_plain_password,
                        new_plain_password, **kwargs):
        service_auth = AuthenticationService(SqlAlchemyUnitOfWork())
        payload = service_auth.authenticate(username, old_plain_password)

        if not payload['c_id'] == kwargs['auth']['c_id']:
            raise self.error_cls("You can't modify someone else password.")
        self.service.modify_password(str(username),
                                     str(old_plain_password),
                                     str(new_plain_password))
