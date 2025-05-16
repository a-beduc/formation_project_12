from domain.model import AuthUser
import infra.repositories as repository


def test_repository_can_retrieve_user(session, init_db_table_users):
    expected = AuthUser(1, 'user_one', 'password_one', False)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get(1)
    assert retrieved == expected


def test_repository_can_retrieve_list_users(session, init_db_table_users):
    expected = [
        AuthUser(1, "user_one", "password_one", False),
        AuthUser(2, "user_two", "password_two", False),
        AuthUser(3, "user_three", "password_three", False)
    ]

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.list()
    assert retrieved == expected


def test_repository_can_save_user(session, init_db_table_users):
    expected = AuthUser(4, 'user_four', 'password_four', True)

    user = AuthUser(4, 'user_four', 'password_four', True)
    repo = repository.SqlAlchemyRepository(session)
    repo.add(user)

    assert repo.get(4) == expected


def test_repository_can_delete_user(session, init_db_table_users):
    expected = [
        AuthUser(1, "user_one", "password_one", False),
        AuthUser(3, "user_three", "password_three", False)
    ]

    user = AuthUser(2, "user_two", "password_two", False)
    repo = repository.SqlAlchemyRepository(session)
    repo.delete(user)

    assert repo.list() == expected


def test_repository_can_update_user(session, init_db_table_users):
    # Might have a problem when updating primary key, may want to prevent
    # PK modifications
    expected = AuthUser(2, "modified_username", "modified_password", True)

    user = AuthUser(2, "modified_username", "modified_password", True)
    repo = repository.SqlAlchemyRepository(session)
    repo.update(user)

    assert repo.get(2) == expected


def test_user_saved_and_loaded_are_equals(session, init_db_table_users):
    user = AuthUser(4, 'user_four', 'password_four', True)
    repo = repository.SqlAlchemyRepository(session)
    repo.add(user)

    assert repo.get(4) == user
