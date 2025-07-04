import pytest

from ee_crm.controllers.app.collaborator import CollaboratorManager
from ee_crm.controllers.app.user import UserManager
from ee_crm.controllers.auth.permission import AuthorizationDenied
from ee_crm.services.app.collaborators import CollaboratorService, \
    CollaboratorServiceError
from ee_crm.services.app.users import UserService
from ee_crm.services.dto import CollaboratorDTO


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    mock = mocker.Mock()
    mocker.patch('ee_crm.controllers.app.collaborator.setup_file_logger',
                 return_value=mock)
    mocker.patch('ee_crm.controllers.app.contract.log_sentry_message_event',
                 return_value=mock)


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow):
    mocker.patch("ee_crm.controllers.auth.permission.DEFAULT_UOW",
                 return_value=in_memory_uow())
    mocker.patch("ee_crm.controllers.app.collaborator.DEFAULT_UOW",
                 return_value=in_memory_uow())
    mocker.patch("ee_crm.controllers.app.user.DEFAULT_UOW",
                 return_value=in_memory_uow())


def test_read_all_collaborator(init_db_table_collaborator,
                               bypass_permission_manager,
                               in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    list_collaborator = controller.read()
    assert list_collaborator is not None
    assert len(list_collaborator) == 4
    assert isinstance(list_collaborator[0], CollaboratorDTO)
    assert list_collaborator[0].first_name == "col_fn_one"
    assert list_collaborator[0].role == 'MANAGEMENT'


def test_filter_collaborator_role_explicit(init_db_table_collaborator,
                                           bypass_permission_manager,
                                           in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    filters = {
        "role": "SUPPORT"
    }
    list_collaborator = controller.read(filters=filters)
    assert list_collaborator is not None
    assert isinstance(list_collaborator[0], CollaboratorDTO)
    assert list_collaborator[0].first_name == "col_fn_thr"


def test_filter_collaborator_role_number(init_db_table_collaborator,
                                         bypass_permission_manager,
                                         in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    filters = {
        "role": "5"
    }
    list_collaborator = controller.read(filters=filters)
    assert list_collaborator is not None
    assert isinstance(list_collaborator[0], CollaboratorDTO)
    assert list_collaborator[0].first_name == "col_fn_thr"


def test_filter_collaborator_role_unknown(init_db_table_collaborator,
                                          bypass_permission_manager,
                                          in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    filters = {
        "role": "UNKNOWN"
    }
    list_collaborator = controller.read(filters=filters)

    assert len(list_collaborator) == 0


def test_filter_collaborator_unknown_filter(init_db_table_collaborator,
                                            bypass_permission_manager,
                                            in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    filters = {
        "unknown": "data"
    }
    with pytest.raises(CollaboratorServiceError,
                       match="No valid filters for Collaborator in {}"):
        controller.read(filters=filters)


def test_sort_collaborator_reverse(init_db_table_collaborator,
                                   bypass_permission_manager,
                                   in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    sort = (("role", True),)
    list_collaborator = controller.read(sort=sort)

    assert len(list_collaborator) == 4
    assert list_collaborator[0].first_name == "col_fn_thr"
    assert list_collaborator[1].first_name == "col_fn_fou"
    assert list_collaborator[2].first_name == "col_fn_two"
    assert list_collaborator[3].first_name == "col_fn_one"


def test_sort_collaborator_unknown_sort(init_db_table_collaborator,
                                        bypass_permission_manager,
                                        in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    sort = (("Unknown", False),)
    with pytest.raises(CollaboratorServiceError,
                       match=r"wrong sort key in \['Unknown'\]"):
        controller.read(sort=sort)


def test_create_collaborator_minimal(init_db_table_users,
                                     init_db_table_collaborator,
                                     bypass_permission_manager,
                                     in_memory_uow):
    controller_coll = CollaboratorManager(CollaboratorService(in_memory_uow()))

    assert len(controller_coll.read()) == 4

    username = "Bobby"
    plain_password = "Password1"
    controller_coll.create(username, plain_password)
    new_collaborator = controller_coll.read()[-1]

    controller_user = UserManager(UserService(in_memory_uow()))
    new_user = controller_user.read(5)[0]

    assert new_user.username == "Bobby"
    assert new_user.id == 5

    assert len(controller_coll.read()) == 5
    assert new_collaborator.user_id == 5
    assert new_collaborator.role == 'DEACTIVATED'


def test_update_collaborator(init_db_table_collaborator,
                             bypass_permission_sales,
                             in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    data = {"last_name": "new_last_name"}
    controller.update(pk=2, **data)

    collaborator = controller.read(2)[0]

    assert collaborator.last_name == "new_last_name"


def test_update_collaborator_not_self(init_db_table_collaborator,
                                      bypass_permission_sales,
                                      in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    data = {"last_name": "new_last_name"}
    with pytest.raises(AuthorizationDenied,
                       match=r"Permission error \(ABAC\) in "
                             r"\(is_management or is_self\)"):
        controller.update(pk=1, **data)


def test_delete_collaborator(init_db_table_users,
                             init_db_table_collaborator,
                             bypass_permission_manager,
                             in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))
    list_collaborator = controller.read()

    assert len(list_collaborator) == 4
    controller.delete(pk=3)

    list_collaborator = controller.read()
    assert len(list_collaborator) == 3


def test_change_collaborator_role(init_db_table_collaborator,
                                  bypass_permission_manager,
                                  in_memory_uow):
    controller = CollaboratorManager(CollaboratorService(in_memory_uow()))

    coll_3 = controller.read(3)[0]
    assert coll_3.role == 'SUPPORT'

    controller.change_collaborator_role(3, "SALES")
    coll_3 = controller.read(3)[0]
    assert coll_3.role == 'SALES'
