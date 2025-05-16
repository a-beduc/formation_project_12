from domain.model import AuthUser


class TestAuthUserOrm:
    def test_auth_user_mapper_can_load_rows(self, session,
                                            init_db_table_users):
        expected = [
            AuthUser(1, "user_one", "password_one", False),
            AuthUser(2, "user_two", "password_two", False),
            AuthUser(3, "user_three", "password_three", False)
        ]
        assert session.query(AuthUser).all() == expected

    def test_auth_user_mapper_can_select_row(self, session,
                                             init_db_table_users):
        expected = AuthUser(1, "user_one", "password_one", False)
        user_id_1 = 1
        assert session.query(AuthUser).filter_by(
            id=user_id_1).one() == expected

        expected = AuthUser(2, "user_two", "password_two", False)
        user_id_2 = 2
        assert session.query(AuthUser).filter_by(
            id=user_id_2).one() == expected

    def test_auth_user_mapper_can_add_row(self, session, init_db_table_users):
        expected = [
            AuthUser(1, "user_one", "password_one", False),
            AuthUser(2, "user_two", "password_two", False),
            AuthUser(3, "user_three", "password_three", False),
            AuthUser(4, "user_four", "password_four", False)
        ]
        new_user = AuthUser(4, "user_four", "password_four", False)
        session.add(new_user)
        session.commit()
        assert session.query(AuthUser).all() == expected

    def test_auth_user_mapper_can_update_row(self, session,
                                             init_db_table_users):
        expected = AuthUser(2, "modified_username", "modified_password", False)

        user_to_update = session.get(AuthUser, 2)
        user_to_update.username = "modified_username"
        user_to_update.password = "modified_password"
        session.commit()

        assert session.get(AuthUser, 2) == expected

    def test_auth_user_mapper_can_delete_row(self, session,
                                             init_db_table_users):
        expected = [
            AuthUser(1, "user_one", "password_one", False),
            AuthUser(2, "user_two", "password_two", False),
        ]
        user_to_remove = session.get(AuthUser, 3)
        session.delete(user_to_remove)
        session.commit()
        assert session.query(AuthUser).all() == expected
