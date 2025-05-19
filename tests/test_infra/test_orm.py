from domain.model import AuthUser, Role, Collaborator, Client, Contract, Event


class TestAuthUserOrm:
    def test_auth_user_mapper_can_load_rows(self, session,
                                            init_db_table_users):
        expected = [
            AuthUser(username="user_one", password="password_one"),
            AuthUser(username="user_two", password="password_two"),
            AuthUser(username="user_thr", password="password_thr")
        ]
        for elem, user in enumerate(expected):
            user.id = elem + 1

        assert session.query(AuthUser).all() == expected

    def test_auth_user_mapper_can_select_row(self, session,
                                             init_db_table_users):
        expected = AuthUser(username="user_one", password="password_one")
        expected.id = 1
        user_id_1 = 1
        assert session.get(AuthUser, user_id_1) == expected

        expected = AuthUser(username="user_two", password="password_two")
        expected.id = 2
        user_id_2 = 2
        assert session.get(AuthUser, user_id_2) == expected

    def test_auth_user_mapper_can_add_row(self, session, init_db_table_users):
        expected = [
            AuthUser(username="user_one", password="password_one"),
            AuthUser(username="user_two", password="password_two"),
            AuthUser(username="user_thr", password="password_thr"),
            AuthUser(username="user_fou", password="password_fou")
        ]
        for elem, user in enumerate(expected):
            user.id = elem + 1

        new_user = AuthUser(username="user_fou", password="password_fou")
        session.add(new_user)
        session.commit()
        assert session.query(AuthUser).all() == expected

    def test_auth_user_mapper_can_update_row(self, session,
                                             init_db_table_users):
        expected = AuthUser(username="modified_username", password="modified_password")
        expected.id = 2

        user_to_update = session.get(AuthUser, 2)
        user_to_update.username = "modified_username"
        user_to_update.password = "modified_password"
        session.commit()

        assert session.get(AuthUser, 2) == expected

    def test_auth_user_mapper_can_delete_row(self, session,
                                             init_db_table_users):
        expected = [
            AuthUser(username="user_one", password="password_one"),
            AuthUser(username="user_two", password="password_two"),
        ]
        for elem, user in enumerate(expected):
            user.id = elem + 1

        user_to_remove = session.get(AuthUser, 3)
        session.delete(user_to_remove)
        session.commit()
        assert session.query(AuthUser).all() == expected


class TestRoleOrm:
    def test_role_mapper_can_load_rows(self, session,
                                       init_db_table_role):
        expected = [
            Role(role="Deactivated"),
            Role(role="Admin"),
            Role(role="Management"),
            Role(role="Sales"),
            Role(role="Support")
        ]
        for elem, role in enumerate(expected):
            role.id = elem + 1

        assert session.query(Role).all() == expected

    def test_role_mapper_can_select_row(self, session,
                                        init_db_table_role):
        expected = Role(role="Deactivated")
        expected.id = 1

        assert session.get(Role, 1) == expected


class TestCollaboratorOrm:
    def test_collaborator_mapper_can_load_rows(self, session,
                                               init_db_table_users,
                                               init_db_table_role,
                                               init_db_table_collaborator):
        expected = [
            Collaborator(last_name='col_ln_one', first_name='col_fn_one',
                         email='col_email@one', phone_number='0000000001',
                         role_id=3,
                         user_id=1),
            Collaborator(last_name='col_ln_two', first_name='col_fn_two',
                         email='col_email@two', phone_number='0000000002',
                         role_id=4,
                         user_id=2),
            Collaborator(last_name='col_ln_thr', first_name='col_fn_thr',
                         email='col_email@thr', phone_number='0000000003',
                         role_id=5,
                         user_id=3),
        ]
        for elem, collaborator in enumerate(expected):
            collaborator.id = elem + 1
        assert session.query(Collaborator).all() == expected

    def test_collaborator_mapper_can_select_row(self, session,
                                                init_db_table_users,
                                                init_db_table_role,
                                                init_db_table_collaborator):
        expected = [
            Collaborator(last_name='col_ln_one', first_name='col_fn_one',
                         email='col_email@one', phone_number='0000000001',
                         role_id=3,
                         user_id=1),
            Collaborator(last_name='col_ln_two', first_name='col_fn_two',
                         email='col_email@two', phone_number='0000000002',
                         role_id=4,
                         user_id=2),
            Collaborator(last_name='col_ln_thr', first_name='col_fn_thr',
                         email='col_email@thr', phone_number='0000000003',
                         role_id=5,
                         user_id=3),
        ]
        for elem, collaborator in enumerate(expected):
            collaborator.id = elem + 1
        assert session.query(Collaborator).all() == expected
        assert session.get(Collaborator, 1) == expected[0]
        assert session.get(Collaborator, 2) == expected[1]
        assert session.get(Collaborator, 3) == expected[2]

    def test_collaborator_mapper_can_add_row(self, session,
                                             init_db_table_users,
                                             init_db_table_role,
                                             init_db_table_collaborator):

        new_collaborator = Collaborator(
            last_name='col_ln_fou', first_name='col_fn_fou',
            email='col_email@fou', phone_number='0000000004', user_id=4)

        session.add(new_collaborator)
        session.commit()
        assert session.get(Collaborator, 4) == new_collaborator

    def test_collaborator_mapper_can_update_row(self, session,
                                                init_db_table_users,
                                                init_db_table_role,
                                                init_db_table_collaborator):

        collaborator = Collaborator(last_name='col_ln_two',
                                    first_name='col_fn_two',
                                    email='col_email@two',
                                    phone_number='0000000002',
                                    role_id=4,
                                    user_id=2)
        collaborator.id = 2

        collaborator.last_name = 'new_col_ln_two'
        collaborator.first_name = 'new_col_fn_two'
        collaborator.email = 'new_col_email@two'

        session.merge(collaborator)
        session.commit()
        assert session.get(Collaborator, 2).last_name == 'new_col_ln_two'

    def test_collaborator_mapper_can_delete_row(self, session,
                                                init_db_table_users,
                                                init_db_table_role,
                                                init_db_table_collaborator):
        session.delete(session.get(Collaborator, 2))
        session.commit()
        assert session.get(Collaborator, 2) is None


# see later if it's useful to test other tables
