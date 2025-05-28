from services.unit_of_work import SqlAlchemyUnitOfWork
from services.app.collaborators import CollaboratorService
from services.app.users import UserService
from controllers.permission import permission


@permission
def who_am_i(**kwargs):
    uow = SqlAlchemyUnitOfWork()
    c_id = kwargs['auth']['c_id']
    collaborator = CollaboratorService(uow).get_collaborator_by_id(c_id)
    user = UserService(uow).get_user_by_id(collaborator.user_id)
    return user, collaborator
