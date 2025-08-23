"""Integration test for ee_crm.controllers.app.client

Fixtures
    in_memory_uow
        Factory that returns a SqlAlchemyUnitOfWork instance linked to
        the in-memory SQLite database.
    init_db_table_collaborator
        create and populate the table linked to the Collaborator model.
    init_db_table_client
        create and populate the table linked to the Client model.
    bypass_permission_manager
        mock the payload returned by decoding a JWT representing a
        specific MANAGER person.
    bypass_permission_sales
        mock the payload returned by decoding a JWT representing a
        specific SALES person.
"""
import pytest

from ee_crm.controllers.app.client import ClientManager
from ee_crm.controllers.auth.permission import AuthorizationDenied
from ee_crm.services.app.clients import ClientService
from ee_crm.services.dto import ClientDTO


@pytest.fixture(autouse=True)
def mock_uow(mocker, in_memory_uow):
    """Fixture to replace the Unit of Work class imported by the
    module for one connected to the SQLite in-memory database.

    Autouse is set to True to avoid to forget to add it when testing.
    """
    mocker.patch("ee_crm.controllers.auth.permission.DEFAULT_UOW",
                 return_value=in_memory_uow())
    mocker.patch("ee_crm.controllers.app.client.DEFAULT_UOW",
                 return_value=in_memory_uow())


def test_read_all_client(init_db_table_client, bypass_permission_manager,
                         in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    list_client = controller.read()
    assert list_client is not None
    assert len(list_client) == 4
    assert isinstance(list_client[0], ClientDTO)
    assert list_client[0].first_name == "cli_fn_one"


def test_filter_client_salesman_id(init_db_table_client,
                                   bypass_permission_manager,
                                   in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    filters = {"salesman_id": "2"}
    list_client = controller.read(filters=filters)

    assert list_client is not None
    assert len(list_client) == 2
    assert list_client[0].first_name == "cli_fn_two"


def test_sort_client_salesman_id_reverse(init_db_table_client,
                                         bypass_permission_manager,
                                         in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    sort = (("salesman_id", True),)
    list_client = controller.read(sort=sort)

    assert list_client is not None
    assert len(list_client) == 4
    assert list_client[0].first_name == "cli_fn_two"
    assert list_client[1].first_name == "cli_fn_thr"
    assert list_client[2].first_name == "cli_fn_one"
    assert list_client[3].first_name == "cli_fn_fou"


def test_sort_client_salesman_id(init_db_table_client,
                                 bypass_permission_manager,
                                 in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    sort = (("salesman_id", False),)
    list_client = controller.read(sort=sort)

    assert list_client is not None
    assert len(list_client) == 4
    assert list_client[0].first_name == "cli_fn_fou"
    assert list_client[1].first_name == "cli_fn_one"
    assert list_client[2].first_name == "cli_fn_two"
    assert list_client[3].first_name == "cli_fn_thr"


def test_create_client_minimal(init_db_table_collaborator,
                               init_db_table_client,
                               bypass_permission_sales,
                               in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))

    list_client = controller.read()
    assert len(list_client) == 4

    controller.create()

    list_client = controller.read()
    assert len(list_client) == 5
    assert list_client[4].salesman_id == 2


def test_create_client_with_data(init_db_table_collaborator,
                                 init_db_table_client,
                                 bypass_permission_sales,
                                 in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))

    list_client = controller.read()
    assert len(list_client) == 4

    data = {"last_name": "bob",
            "first_name": "ross",
            "email": "painter@mail.c",
            "phone_number": "09 65 48 98 78",
            "company": "The Company"}
    controller.create(**data)

    list_client = controller.read()
    assert len(list_client) == 5
    assert list_client[4].last_name == "bob"
    assert list_client[4].first_name == "ross"
    assert list_client[4].email == "painter@mail.c"
    assert list_client[4].phone_number == "09 65 48 98 78"
    assert list_client[4].company == "The Company"


def test_update_client_with_data(init_db_table_collaborator,
                                 init_db_table_client,
                                 bypass_permission_sales,
                                 in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    data = {"last_name": "bob",
            "first_name": "ross",
            "unwanted_data": "fdasfasf"}

    client_2 = controller.read(2)

    assert client_2[0].last_name == 'cli_ln_two'
    assert client_2[0].first_name == 'cli_fn_two'

    controller.update(pk=2, **data)

    client_2_updated = controller.read(2)

    assert client_2[0] != client_2_updated[0]
    assert client_2_updated[0].last_name == data['last_name']
    assert client_2_updated[0].first_name == data['first_name']


def test_update_client_not_my_client(init_db_table_collaborator,
                                     init_db_table_client,
                                     bypass_permission_sales,
                                     in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    data = {"last_name": "bob",
            "first_name": "ross",
            "unwanted_data": "fdasfasf"}

    with pytest.raises(
            AuthorizationDenied,
            match=r"Permission error \(ABAC\) in "
                  r"\(is_client_associated_salesman or "
                  r"\(is_management and not client_has_salesman\)\)"):
        controller.update(pk=1, **data)


def test_update_client_empty_data(init_db_table_collaborator,
                                  init_db_table_client,
                                  bypass_permission_sales,
                                  in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    client_before = controller.read(2)[0]
    controller.update(pk=2)
    client_after = controller.read(2)[0]
    assert client_before == client_after


def test_delete_client_ok(init_db_table_collaborator,
                          init_db_table_client,
                          bypass_permission_sales,
                          in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    list_client_before = controller.read()
    assert len(list_client_before) == 4

    controller.delete(2)

    list_client_after = controller.read()
    assert len(list_client_after) == 3


def test_delete_not_my_client_o(init_db_table_collaborator,
                                init_db_table_client,
                                bypass_permission_sales,
                                in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    list_client_before = controller.read()
    assert len(list_client_before) == 4
    with pytest.raises(
            AuthorizationDenied,
            match=r"Permission error \(ABAC\) in "
                  r"\(is_client_associated_salesman or "
                  r"\(is_management and not client_has_salesman\)\)"):
        controller.delete(1)

    list_client_after = controller.read()
    assert len(list_client_after) == 4


def test_user_associated_clients(init_db_table_collaborator,
                                 init_db_table_client,
                                 bypass_permission_sales,
                                 in_memory_uow):
    controller = ClientManager(ClientService(in_memory_uow()))
    clients = controller.user_associated_resource(sort=None, filters=None)

    assert len(clients) == 2
    assert clients[0].id == 2
    assert clients[1].id == 3


def test_orphan_clients(init_db_table_collaborator,
                        init_db_table_client,
                        bypass_permission_sales,
                        in_memory_uow):

    controller = ClientManager(ClientService(in_memory_uow()))
    clients = controller.orphan_clients(sort=None, filters=None)

    assert len(clients) == 1
    assert clients[0].id == 4
