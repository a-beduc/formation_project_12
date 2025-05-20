import argon2
import re
from domain.model import AuthUser


ph = argon2.PasswordHasher()


class AuthError(Exception):
    pass


def valid_password(plain_password):
    return (
        len(plain_password) >= 8 and
        re.search(r"[A-Z]", plain_password) and
        re.search(r"[a-z]", plain_password) and
        re.search(r"\d", plain_password)
    )


def valid_username(uow, username):
    return len(username) >= 3 and not uow.users.get_by_username(username)


def create_user(uow, username, plain_password):
    if not valid_password(plain_password):
        raise AuthError("weak password")

    with uow:
        if not valid_username(uow, username):
            raise AuthError("username too short or already in use")

        password_hash = ph.hash(plain_password)
        user = AuthUser(username=username, password=password_hash)
        uow.users.add(user)
        uow.commit()


def login(uow, username, plain_password):
    with uow:
        user = uow.users.get_by_username(username)
        if user is None:
            raise AuthError(f"User not found with {username}")

        password_hash = user.password
        try:
            ph.verify(password_hash, plain_password)
            return user
        except argon2.exceptions.VerifyMismatchError:
            raise AuthError(f"Password mismatch")
