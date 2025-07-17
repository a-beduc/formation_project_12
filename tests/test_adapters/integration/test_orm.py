"""Integration tests for ee_crm.adapters.orm

Tests to verify that dynamically created relationship behave as expected.
It might be redundant with SQLAlchemy tests, but it assures that the
addon behaves as needed.
"""
import datetime

from ee_crm.domain.model import AuthUser, Collaborator, Client


class TestRelationship:
    """Class to test if relationship attributes are properly initiated
    through orm."""

    def test_user_to_collaborator_and_back(self, session,
                                           init_db_table_users,
                                           init_db_table_collaborator):
        """Verify that mapping is working as expected and provides
        dynamically defined attributes to link models AuthUser and
        Collaborator."""
        user = session.get(AuthUser, 1)
        collaborator = session.get(Collaborator, 1)

        assert user.collaborator == collaborator
        assert collaborator.user == user

    def test_update_collaborator_user_update_collaborator_user_id(
            self, session,
            init_db_table_users,
            init_db_table_collaborator):
        """Verify that mapping is working as expected and that
        dynamically defined attributes can be updated and change the
        expected attributes for the linked resource.
        id if we modify Collaborator.user, AuthUser.collaborator is
        updated accordingly."""
        new_user = AuthUser(_username="test_user", _password="test_password")
        session.add(new_user)
        session.commit()

        # user without a collaborator.
        user_fiv = session.get(AuthUser, 5)
        assert user_fiv.username == new_user.username

        # collaborator already linked to user 1.
        collaborator = session.get(Collaborator, 1)
        assert collaborator.user_id == 1

        # link collaborator to user 5.
        # if collaborator.user is modified session.commit() is needed to update
        collaborator.user = user_fiv
        session.commit()
        assert collaborator.user_id == 5
        assert user_fiv.collaborator == collaborator

    def test_update_collaborator_user_id_update_collaborator_user(
            self, session,
            init_db_table_users,
            init_db_table_collaborator):
        """Verify that mapping is working as expected and that
        static attributes can be updated and change the linked
        dynamic attributes.
        ie if we modify collaborator._user_id, collaborator.user is also
        updated."""
        new_user = AuthUser(_username="test_user", _password="test_password")
        session.add(new_user)

        user_fiv = session.get(AuthUser, 5)
        assert user_fiv == new_user

        collaborator = session.get(Collaborator, 1)
        assert collaborator.user_id == 1

        collaborator._user_id = new_user.id
        # if collaborator.user_id is modified, session.commit isn't needed
        assert collaborator.user == user_fiv

    def test_delete_user_and_get_collaborator_user(self, session,
                                                   init_db_table_users,
                                                   init_db_table_collaborator):
        """Verify that mapping is working as expected and that
        dynamically defined attributes can be deleted and update
        corresponding attributes of the linked resource."""
        collaborator = session.get(Collaborator, 1)
        user = session.get(AuthUser, 1)
        session.delete(user)
        session.commit()

        assert collaborator.user_id is None
        assert collaborator.user is None

    def test_delete_collaborator_and_get_user_collaborator(
            self, session, init_db_table_users, init_db_table_collaborator):
        """Verify that mapping is working as expected and that if a
        linked resource is deleted, the object in memory that refer to
        it are also properly updated."""
        collaborator = session.get(Collaborator, 1)
        user = session.get(AuthUser, 1)
        session.delete(collaborator)
        session.commit()

        assert user.collaborator is None

    def test_collaborator_to_client_and_back(self, session,
                                             init_db_table_users,
                                             init_db_table_collaborator,
                                             init_db_table_client):
        """Verify that mapping is working as expected and that
        one-to-many relations are properly working."""
        collaborator_2 = session.get(Collaborator, 2)
        collaborator_3 = session.get(Collaborator, 3)
        client_2 = session.get(Client, 2)
        client_3 = session.get(Client, 3)

        assert collaborator_2.clients == [client_2, client_3]
        assert collaborator_3.clients == []

        assert client_2.salesman == collaborator_2
        assert client_3.salesman == collaborator_2

    def test_add_client_to_salesman(self, session,
                                    init_db_table_users,
                                    init_db_table_collaborator,
                                    init_db_table_client):
        """Verify that mapping is working as expected and that Client
        model seems to work as expected.
        """
        collaborator_2 = session.get(Collaborator, 2)
        client_4 = Client(last_name='col_ln_four',
                          first_name='col_fn_four',
                          email='col_email@four',
                          phone_number='0000000004',
                          company='company_four',
                          _created_at=datetime.datetime.fromisoformat(
                              '2025-01-01 00:00:04'),
                          _updated_at=datetime.datetime.fromisoformat(
                              '2025-02-01 00:00:04'),
                          _salesman_id=None)
        session.add(client_4)
        collaborator_2.clients.append(client_4)

        client_2 = session.get(Client, 2)
        client_3 = session.get(Client, 3)

        assert collaborator_2.clients == [client_2, client_3, client_4]

        assert client_2.salesman == collaborator_2
        assert client_3.salesman == collaborator_2
        assert client_4.salesman == collaborator_2

        # commit necessary to update salesman_id in client_4
        session.commit()
        assert client_2.salesman_id == collaborator_2.id
        assert client_3.salesman_id == collaborator_2.id
        assert client_4.salesman_id == collaborator_2.id

# see later if it's useful to test other tables
