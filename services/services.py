class AuthError(Exception):
    pass


def login(uow, username, password):
    # temporary function to test uow pattern
    with uow:
        user = uow.users.get_by_username(username)
        if user is None:
            raise AuthError(f"User not found with {username}")
        if user.password != password:
            raise AuthError(f"Invalid password")
        return user
