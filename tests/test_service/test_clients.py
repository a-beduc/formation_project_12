import pytest

from ee_crm.domain.model import Collaborator, Client
from ee_crm.services.app.clients import ClientService, ClientServiceError


@pytest.fixture
def init_uow(uow, fake_repo):
    coll_a = Collaborator(first_name="fn_a", last_name="ln_a", _role_id=4,
                          _user_id=1)
    coll_b = Collaborator(first_name="fn_b", last_name="ln_b", _role_id=4,
                          _user_id=2)
    coll_c = Collaborator(first_name="fn_c", last_name="ln_c", _role_id=3,
                          _user_id=3)
    uow.collaborators = fake_repo(init=(coll_a, coll_b, coll_c))

    cli_a = Client(last_name="cl_ln_a", first_name="cl_fn_a", _salesman_id=1)
    cli_b = Client(last_name="cl_ln_b", first_name="cl_fn_b", _salesman_id=1)
    cli_c = Client(last_name="cl_ln_c", first_name="cl_fn_c", _salesman_id=2)
    cli_d = Client(last_name="cl_ln_d", first_name="cl_fn_d", _salesman_id=2)
    cli_e = Client(last_name="cl_ln_e", first_name="cl_fn_e", _salesman_id=2)
    uow.clients = fake_repo(init=(cli_a, cli_b, cli_c, cli_d, cli_e))
    return uow


class TestClientCRUD:
    def test_client_creation_success(self, init_uow):
        client_data = {
            "salesman_id": 1,
            "last_name": "new_last_name",
            "first_name": "new_first_name",
        }

        service = ClientService(init_uow)
        service.create(**client_data)
        assert init_uow.commited is True

        client = init_uow.clients.get(6)
        assert client.salesman_id == 1
        assert client.last_name == "new_last_name"
        assert client.first_name == "new_first_name"
        assert client.id == 6

    def test_client_creation_failure_not_salesman(self, mocker, init_uow):
        client_data = {
            "last_name": "new_last_name",
            "first_name": "new_first_name",
            "unused_payload": "whatever_data",
            "salesman_id": 3
        }
        service = ClientService(init_uow)
        spy_uow_rollback = mocker.spy(init_uow, "rollback")

        with pytest.raises(ClientServiceError,
                           match="Only sales people can create clients"
                           ):
            service.create(**client_data)

        assert spy_uow_rollback.call_count == 1

    def test_client_uow_error(self, mocker, init_uow):
        client_data = {
            "last_name": "new_last_name",
            "first_name": "new_first_name",
            "unused_payload": "whatever_data",
            "salesman_id": 1
        }

        def uow_error():
            raise RuntimeError('db crash')

        mocker.patch.object(init_uow, "commit", uow_error)
        service = ClientService(init_uow)
        spy_uow_rollback = mocker.spy(init_uow, "rollback")

        with pytest.raises(RuntimeError):
            service.create(**client_data)

        # rollback called twice because ClientService.create call an uow
        # ctxt manager to do a verification before opening the one to create.
        assert spy_uow_rollback.call_count == 2

    def test_get_client_success(self, init_uow):
        client_id = 1
        service = ClientService(init_uow)
        client_dto = service.retrieve(client_id)

        assert client_dto[0].salesman_id == 1
        assert client_dto[0].id == 1

    def test_get_client_failure(self, init_uow):
        client_id = 10
        service = ClientService(init_uow)
        with pytest.raises(ClientServiceError, match="Client not found"):
            service.retrieve(client_id)

    def test_get_all_clients_success(self, init_uow):
        client_id = 1
        service = ClientService(init_uow)
        list_clients = service.retrieve_all()

        client_dto = service.retrieve(client_id)

        assert list_clients[0] == client_dto[0]
        assert len(list_clients) == 5

    def test_filter_salesman_clients(self, init_uow):
        service = ClientService(init_uow)
        salesman_id = 2
        list_clients = service.filter(salesman_id=salesman_id)

        assert len(list_clients) == 3
        assert list_clients[0].id == 3
        assert list_clients[0].last_name == "cl_ln_c"

        salesman_id = 3
        list_clients = service.filter(salesman_id=salesman_id)

        assert len(list_clients) == 0
        assert list_clients == tuple()

    def test_delete_client(self, init_uow):
        service = ClientService(init_uow)
        client_id = 1

        assert service.retrieve(client_id)[0] is not None
        service.remove(client_id)

        assert init_uow.commited is True

        with pytest.raises(ClientServiceError, match="Client not found"):
            service.retrieve(client_id)

    def test_update_client(self, init_uow):
        service = ClientService(init_uow)
        client_id = 1
        update_input = {"last_name": "new_last_name", "useless_data": "whatever"}
        service.modify(client_id, **update_input)

        assert init_uow.commited is True
        assert service.retrieve(client_id)[0].last_name == "new_last_name"

    def test_sort_clients_by_reverse_salesman_id(self, init_uow):
        service = ClientService(init_uow)
        all_clients = service.retrieve_all(sort=(('salesman_id', True),))

        assert all_clients[0].last_name == "cl_ln_c"
        assert all_clients[1].last_name == "cl_ln_d"
        assert all_clients[2].last_name == "cl_ln_e"
        assert all_clients[3].last_name == "cl_ln_a"
        assert all_clients[4].last_name == "cl_ln_b"

    def test_sort_clients_by_wrong_key(self, init_uow):
        service = ClientService(init_uow)

        with pytest.raises(ClientServiceError,
                           match=r"wrong sort key in \['unknown_key'\]"):
            service.retrieve_all(sort=(('unknown_key', True),))
