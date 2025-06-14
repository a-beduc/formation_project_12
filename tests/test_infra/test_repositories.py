from ee_crm.domain.model import AuthUser, Collaborator
import ee_crm.adapters.repositories as repository


def test_repository_can_retrieve_user(session, init_db_table_users):
    expected = AuthUser(_username='user_one', _password='password_one')
    expected.id = 1

    repo = repository.SqlAlchemyUserRepository(session)
    retrieved = repo.get(1)
    assert retrieved == expected


def test_repository_can_retrieve_list_users(session, init_db_table_users):
    expected = [
        AuthUser(_username="user_one", _password="password_one"),
        AuthUser(_username="user_two", _password="password_two"),
        AuthUser(_username="user_thr", _password="password_thr"),
        AuthUser(_username="user_fou", _password="password_fou"),
    ]
    for elem, user in enumerate(expected):
        user.id = elem + 1

    repo = repository.SqlAlchemyUserRepository(session)
    retrieved = repo.list()
    assert retrieved == expected


def test_repository_can_save_user(session, init_db_table_users):
    expected = AuthUser(_username='user_fiv', _password='password_fiv')
    expected.id = 5

    user = AuthUser(_username='user_fiv', _password='password_fiv')
    repo = repository.SqlAlchemyUserRepository(session)
    repo.add(user)

    assert repo.get(5) == expected


def test_repository_can_delete_user(session, init_db_table_users):
    expected = [
        AuthUser(_username="user_one", _password="password_one"),
        AuthUser(_username="user_thr", _password="password_thr"),
        AuthUser(_username="user_fou", _password="password_fou")
    ]
    expected[0].id, expected[1].id, expected[2].id = (1, 3, 4)

    user = AuthUser(_username="user_two", _password="password_two")
    user.id = 2

    repo = repository.SqlAlchemyUserRepository(session)
    repo.delete(2)

    assert repo.list() == expected


def test_repository_can_update_user(session, init_db_table_users):
    expected = AuthUser(_username="modified_username",
                        _password="modified_password")
    expected.id = 2

    repo = repository.SqlAlchemyUserRepository(session)
    user = repo.get(2)
    user.username = "modified_username"
    user._password = "modified_password"

    assert repo.get(2) == expected


def test_user_saved_and_loaded_are_equals(session, init_db_table_users):
    in_memory_user = AuthUser(_username='user_fiv', _password='password_fiv')
    repo = repository.SqlAlchemyUserRepository(session)
    repo.add(in_memory_user)

    in_memory_user.id = 5

    assert repo.get(5) == in_memory_user
    assert id(repo.get(5)) == id(in_memory_user)


def test_repository_can_get_user_from_username(session,
                                               init_db_table_users):
    username = "user_one"
    repo = repository.SqlAlchemyUserRepository(session)
    user = repo.filter_one(username=username)

    assert user is not None
    assert user.username == username


def test_repository_can_retrieve_collaborator(session,
                                              init_db_table_collaborator):
    expected = Collaborator(last_name='col_ln_one',
                            first_name='col_fn_one',
                            email='col_email@one',
                            phone_number='0000000001',
                            _role_id=3, _user_id=1)
    expected.id = 1

    repo = repository.SqlAlchemyCollaboratorRepository(session)
    retrieved = repo.get(1)
    assert retrieved == expected


def test_collaborator_saved_and_loaded_are_equals(session,
                                                  init_db_table_users):
    in_memory_collaborator = Collaborator(
        last_name='col_ln_fou', first_name='col_fn_fou',
        email='col_email@fou', phone_number='0000000004', _user_id=4)
    repo = repository.SqlAlchemyCollaboratorRepository(session)
    repo.add(in_memory_collaborator)

    in_memory_collaborator.id = 4

    assert repo.get(4) == in_memory_collaborator


def test_collaborator_can_be_filtered_by_role(session,
                                              init_db_table_users,
                                              init_db_table_collaborator):
    collaborator = Collaborator(last_name='col_ln_one',
                                first_name='col_fn_one',
                                email='col_email@one',
                                phone_number='0000000001',
                                _role_id=3, _user_id=1)
    collaborator.id = 1
    expected = [collaborator]
    repo = repository.SqlAlchemyCollaboratorRepository(session)
    retrieved = repo.filter(role=3)
    assert retrieved == expected


def test_collaborator_can_be_filtered_with_multiple_fields(
        session, init_db_table_users, init_db_table_collaborator):
    collaborator = Collaborator(last_name='col_ln_one',
                                first_name='col_fn_one',
                                email='col_email@one',
                                phone_number='0000000001',
                                _role_id=3, _user_id=1)
    collaborator.id = 1
    expected = collaborator
    repo = repository.SqlAlchemyCollaboratorRepository(session)
    retrieved = repo.filter_one(role=3, user_id=1)
    assert retrieved == expected


def test_collaborator_can_be_sorted_by_reverse_user_id(
        session, init_db_table_collaborator):
    repo = repository.SqlAlchemyCollaboratorRepository(session)
    expected = repo.list()[::-1]
    retrieved = repo.list(sort=(("user_id", True),))
    assert retrieved == expected


def test_contract_can_be_sorted_by_signed(session, init_db_table_contract):
    repo = repository.SqlAlchemyContractRepository(session)
    base_list = repo.list()
    expected = [base_list[2], base_list[3], base_list[0], base_list[1],
                base_list[4], base_list[5]]
    retrieved = repo.list(sort=(("signed", False),))

    assert retrieved == expected


def test_contract_can_be_sorted_by_signed_then_by_reverse_id(
        session, init_db_table_contract):
    repo = repository.SqlAlchemyContractRepository(session)
    base_list = repo.list()
    expected = [base_list[3], base_list[2], base_list[5], base_list[4],
                base_list[1], base_list[0]]
    retrieved = repo.list(sort=(("signed", False), ("id", True)))

    assert retrieved == expected


def test_contract_can_be_filtered_by_signed_reverse_id_sorted(
        session, init_db_table_contract):
    repo = repository.SqlAlchemyContractRepository(session)
    base_list = repo.list()
    expected = [base_list[5], base_list[4], base_list[1], base_list[0]]
    retrieved = repo.filter(sort=(("id", True),), signed=True)

    assert retrieved == expected


def test_can_retrieve_client_from_contract(
        session, init_db_table_client, init_db_table_contract):
    repo_contract = repository.SqlAlchemyContractRepository(session)
    repo_client = repository.SqlAlchemyClientRepository(session)
    contract = repo_contract.get(2)
    client = repo_client.get(2)
    assert client == contract.client


def test_can_retrieve_client_from_event(
        session, init_db_table_event, init_db_table_contract,
        init_db_table_client):
    repo_event = repository.SqlAlchemyEventRepository(session)
    repo_client = repository.SqlAlchemyClientRepository(session)
    event = repo_event.get(2)
    client = repo_client.get(3)
    assert client == event.contract.client
