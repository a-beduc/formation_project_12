from domain.model import AuthUser, Collaborator
import adapters.repositories as repository


def test_repository_can_retrieve_user(session, init_db_table_users):
    expected = AuthUser(username='user_one', password='password_one')
    expected.id = 1

    repo = repository.SqlAlchemyUserRepository(session)
    retrieved = repo.get(1)
    assert retrieved == expected


def test_repository_can_retrieve_list_users(session, init_db_table_users):
    expected = [
        AuthUser(username="user_one", password="password_one"),
        AuthUser(username="user_two", password="password_two"),
        AuthUser(username="user_thr", password="password_thr")
    ]
    for elem, user in enumerate(expected):
        user.id = elem + 1

    repo = repository.SqlAlchemyUserRepository(session)
    retrieved = repo.list()
    assert retrieved == expected


def test_repository_can_save_user(session, init_db_table_users):
    expected = AuthUser(username='user_fou', password='password_fou')
    expected.id = 4

    user = AuthUser(username='user_fou', password='password_fou')
    repo = repository.SqlAlchemyUserRepository(session)
    repo.add(user)

    assert repo.get(4) == expected


def test_repository_can_delete_user(session, init_db_table_users):
    expected = [
        AuthUser(username="user_one", password="password_one"),
        AuthUser(username="user_thr", password="password_thr")
    ]
    expected[0].id, expected[1].id = (1, 3)

    user = AuthUser(username="user_two", password="password_two")
    user.id = 2

    repo = repository.SqlAlchemyUserRepository(session)
    repo.delete(2)

    assert repo.list() == expected


def test_repository_can_update_user(session, init_db_table_users):
    expected = AuthUser(username="modified_username",
                        password="modified_password")
    expected.id = 2

    repo = repository.SqlAlchemyUserRepository(session)
    user = repo.get(2)
    user.username = "modified_username"
    user.password = "modified_password"
    repo.update(user)

    assert repo.get(2) == expected


def test_user_saved_and_loaded_are_equals(session, init_db_table_users):
    in_memory_user = AuthUser(username='user_fou', password='password_fou')
    repo = repository.SqlAlchemyUserRepository(session)
    repo.add(in_memory_user)

    in_memory_user.id = 4

    assert repo.get(4) == in_memory_user
    assert id(repo.get(4)) == id(in_memory_user)


def test_repository_can_get_user_from_username(session,
                                               init_db_table_users):
    username = "user_one"
    repo = repository.SqlAlchemyUserRepository(session)
    user = repo.get_by_username(username)

    assert user is not None
    assert user.username == username


def test_repository_can_retrieve_collaborator(session,
                                              init_db_table_collaborator):
    expected = Collaborator(last_name='col_ln_one',
                            first_name='col_fn_one',
                            email='col_email@one',
                            phone_number='0000000001',
                            role_id=3,
                            user_id=1)
    expected.id = 1

    repo = repository.SqlAlchemyCollaboratorRepository(session)
    retrieved = repo.get(1)
    assert retrieved == expected


def test_collaborator_saved_and_loaded_are_equals(session, init_db_table_users):
    in_memory_collaborator = Collaborator(
        last_name='col_ln_fou', first_name='col_fn_fou',
        email='col_email@fou', phone_number='0000000004', user_id=4)
    repo = repository.SqlAlchemyCollaboratorRepository(session)
    repo.add(in_memory_collaborator)

    in_memory_collaborator.id = 4

    assert repo.get(4) == in_memory_collaborator
