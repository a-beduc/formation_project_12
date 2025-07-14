import datetime

from ee_crm.domain.model import AuthUser, Collaborator, Client


class TestAuthUserOrm:
    def test_auth_user_mapper_can_load_rows(self, session,
                                            init_db_table_users):
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
        expected = AuthUser(_username="user_one", _password="password_one")
        expected.id = 1
        user_id_1 = 1
        assert session.get(AuthUser, user_id_1) == expected

        expected = AuthUser(_username="user_two", _password="password_two")
        expected.id = 2
        user_id_2 = 2
        assert session.get(AuthUser, user_id_2) == expected

    def test_auth_user_mapper_can_add_row(self, session, init_db_table_users):
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
    def test_collaborator_mapper_can_load_rows(self, session,
                                               init_db_table_users,
                                               init_db_table_collaborator):
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
        assert session.get(Collaborator, 1) == expected[0]
        assert session.get(Collaborator, 2) == expected[1]
        assert session.get(Collaborator, 3) == expected[2]
        assert session.get(Collaborator, 4) == expected[3]

    def test_collaborator_mapper_can_add_row(self, session,
                                             init_db_table_users,
                                             init_db_table_collaborator):
        new_collaborator = Collaborator(
            last_name='col_ln_fiv', first_name='col_fn_fiv',
            email='col_email@fiv', phone_number='0000000005', _user_id=5)

        session.add(new_collaborator)
        session.commit()
        assert session.get(Collaborator, 5) == new_collaborator

    def test_collaborator_mapper_can_update_row(self, session,
                                                init_db_table_users,
                                                init_db_table_collaborator):

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
        session.delete(session.get(Collaborator, 2))
        session.commit()
        assert session.get(Collaborator, 2) is None


class TestRelationship:
    def test_user_to_collaborator_and_back(self, session,
                                           init_db_table_users,
                                           init_db_table_collaborator):
        user = session.get(AuthUser, 1)
        collaborator = session.get(Collaborator, 1)

        assert user.collaborator == collaborator
        assert collaborator.user == user

    def test_update_collaborator_user_update_collaborator_user_id(
            self, session,
            init_db_table_users,
            init_db_table_collaborator):
        new_user = AuthUser(_username="test_user", _password="test_password")
        session.add(new_user)
        session.commit()

        user_fiv = session.get(AuthUser, 5)
        assert user_fiv.username == new_user.username

        collaborator = session.get(Collaborator, 1)
        assert collaborator.user_id == 1

        collaborator.user = user_fiv
        # if collaborator.user is modified session.commit() is needed to update
        session.commit()
        assert collaborator.user_id == 5

    def test_update_collaborator_user_id_update_collaborator_user(
            self, session,
            init_db_table_users,
            init_db_table_collaborator):
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
        collaborator = session.get(Collaborator, 1)
        user = session.get(AuthUser, 1)
        session.delete(user)
        session.commit()

        assert collaborator.user_id is None
        assert collaborator.user is None

    def test_delete_collaborator_and_get_user_collaborator(
            self, session, init_db_table_users, init_db_table_collaborator):
        collaborator = session.get(Collaborator, 1)
        user = session.get(AuthUser, 1)
        session.delete(collaborator)
        session.commit()

        assert user.collaborator is None

    def test_collaborator_to_client_and_back(self, session,
                                             init_db_table_users,
                                             init_db_table_collaborator,
                                             init_db_table_client):
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
