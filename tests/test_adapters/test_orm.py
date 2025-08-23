"""Unit tests for ee_crm.adapters.orm

Use a SQLite in-memory database, with a session created and populated
for each test.

The tests don't cover all the tables, might be easily expanded if
it's judged necessary.

Fixtures
    session
        SQLAlchemy session object bound to the in-memory test SQLite
        database.
    init_db_table_users
        create and populate the table linked to the AuthUser model.
    init_db_table_collaborator
        create and populate the table linked to the Collaborator model.
"""
from ee_crm.domain.model import AuthUser, Collaborator


class TestAuthUserOrm:
    """Class to group up tests for AuthUser-related orm functionality."""

    def test_auth_user_mapper_can_load_rows(self, session,
                                            init_db_table_users):
        """Verify that mapping is working as expected and provides
        SQLAlchemy query.all functionality."""
        expected = [
            AuthUser(_username="user_one", _password="password_one"),
            AuthUser(_username="user_two", _password="password_two"),
            AuthUser(_username="user_thr", _password="password_thr"),
            AuthUser(_username="user_fou", _password="password_fou")
        ]
        for elem, user in enumerate(expected):
            user.id = elem + 1

        assert session.query(AuthUser).all() == expected

    def test_auth_user_mapper_can_select_row(self, session,
                                             init_db_table_users):
        """Verify that mapping is working as expected and provides
        SQLAlchemy get functionality."""
        expected = AuthUser(_username="user_one", _password="password_one")
        expected.id = 1
        user_id_1 = 1
        assert session.get(AuthUser, user_id_1) == expected

        expected = AuthUser(_username="user_two", _password="password_two")
        expected.id = 2
        user_id_2 = 2
        assert session.get(AuthUser, user_id_2) == expected

    def test_auth_user_mapper_can_add_row(self, session, init_db_table_users):
        """Verify that mapping is working as expected and provides
        SQLAlchemy add functionality."""
        expected = [
            AuthUser(_username="user_one", _password="password_one"),
            AuthUser(_username="user_two", _password="password_two"),
            AuthUser(_username="user_thr", _password="password_thr"),
            AuthUser(_username="user_fou", _password="password_fou"),
            AuthUser(_username="user_fiv", _password="password_fiv")
        ]
        for elem, user in enumerate(expected):
            user.id = elem + 1

        new_user = AuthUser(_username="user_fiv", _password="password_fiv")
        session.add(new_user)
        session.commit()
        assert session.query(AuthUser).all() == expected

    def test_auth_user_mapper_can_update_row(self, session,
                                             init_db_table_users):
        """Verify that mapping is working as expected and provides
        SQLAlchemy direct update functionality."""
        expected = AuthUser(_username="modified_username",
                            _password="modified_password")
        expected.id = 2

        user_to_update = session.get(AuthUser, 2)
        user_to_update.username = "modified_username"
        user_to_update._password = "modified_password"
        session.commit()

        assert session.get(AuthUser, 2) == expected

    def test_auth_user_mapper_can_delete_row(self, session,
                                             init_db_table_users):
        """Verify that mapping is working as expected and provides
        SQLAlchemy delete functionality."""
        expected = [
            AuthUser(_username="user_one", _password="password_one"),
            AuthUser(_username="user_two", _password="password_two"),
            AuthUser(_username="user_thr", _password="password_thr"),
        ]
        for elem, user in enumerate(expected):
            user.id = elem + 1

        user_to_remove = session.get(AuthUser, 4)
        session.delete(user_to_remove)
        session.commit()
        assert session.query(AuthUser).all() == expected


class TestCollaboratorOrm:
    """Class to group up tests for Collaborator-related orm functionality."""

    def test_collaborator_mapper_can_load_rows(self, session,
                                               init_db_table_users,
                                               init_db_table_collaborator):
        """Verify that mapping is working as expected and provides
        SQLAlchemy query.all functionality."""
        expected = [
            Collaborator(last_name='col_ln_one', first_name='col_fn_one',
                         email='col_email@one', phone_number='0000000001',
                         _role_id=3, _user_id=1),
            Collaborator(last_name='col_ln_two', first_name='col_fn_two',
                         email='col_email@two', phone_number='0000000002',
                         _role_id=4, _user_id=2),
            Collaborator(last_name='col_ln_thr', first_name='col_fn_thr',
                         email='col_email@thr', phone_number='0000000003',
                         _role_id=5, _user_id=3),
            Collaborator(last_name='col_ln_fou', first_name='col_fn_fou',
                         email='col_email@fou', phone_number='0000000004',
                         _role_id=5, _user_id=4),
        ]
        for elem, collaborator in enumerate(expected):
            collaborator.id = elem + 1
        assert session.query(Collaborator).all() == expected

    def test_collaborator_mapper_can_select_row(self, session,
                                                init_db_table_users,
                                                init_db_table_collaborator):
        """Verify that mapping is working as expected and provides
        SQLAlchemy get functionality."""
        expected = [
            Collaborator(last_name='col_ln_one', first_name='col_fn_one',
                         email='col_email@one', phone_number='0000000001',
                         _role_id=3, _user_id=1),
            Collaborator(last_name='col_ln_two', first_name='col_fn_two',
                         email='col_email@two', phone_number='0000000002',
                         _role_id=4, _user_id=2),
            Collaborator(last_name='col_ln_thr', first_name='col_fn_thr',
                         email='col_email@thr', phone_number='0000000003',
                         _role_id=5, _user_id=3),
            Collaborator(last_name='col_ln_fou', first_name='col_fn_fou',
                         email='col_email@fou', phone_number='0000000004',
                         _role_id=5, _user_id=4),
        ]
        for elem, collaborator in enumerate(expected):
            collaborator.id = elem + 1
        assert session.get(Collaborator, 1) == expected[0]
        assert session.get(Collaborator, 2) == expected[1]
        assert session.get(Collaborator, 3) == expected[2]
        assert session.get(Collaborator, 4) == expected[3]

    def test_collaborator_mapper_can_add_row(self, session,
                                             init_db_table_users,
                                             init_db_table_collaborator):
        """Verify that mapping is working as expected and provides
        SQLAlchemy add functionality."""
        new_collaborator = Collaborator(
            last_name='col_ln_fiv', first_name='col_fn_fiv',
            email='col_email@fiv', phone_number='0000000005', _user_id=5)

        session.add(new_collaborator)
        session.commit()
        assert session.get(Collaborator, 5) == new_collaborator

    def test_collaborator_mapper_can_update_row(self, session,
                                                init_db_table_users,
                                                init_db_table_collaborator):
        """Verify that mapping is working as expected and provides
        SQLAlchemy direct update functionality."""
        collaborator = Collaborator(last_name='col_ln_two',
                                    first_name='col_fn_two',
                                    email='col_email@two',
                                    phone_number='0000000002',
                                    _role_id=4, _user_id=2)
        collaborator.id = 2

        collaborator.last_name = 'new_col_ln_two'
        collaborator.first_name = 'new_col_fn_two'
        collaborator.email = 'new_col_email@two'

        session.merge(collaborator)
        session.commit()
        assert session.get(Collaborator, 2).last_name == 'new_col_ln_two'

    def test_collaborator_mapper_can_delete_row(self, session,
                                                init_db_table_users,
                                                init_db_table_collaborator):
        """Verify that mapping is working as expected and provides
        SQLAlchemy delete functionality."""
        session.delete(session.get(Collaborator, 2))
        session.commit()
        assert session.get(Collaborator, 2) is None
