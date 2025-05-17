from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthUser:
    def __init__(self, user_id, username, password, superuser=False):
        self.id = user_id
        self.username = username
        self.password = password
        self.superuser = superuser
    id: int
    username: str
    password: str


@dataclass(frozen=True)
class Role:
    id: int
    role: str


    def __repr__(self):
        return f"<AuthUser {self.id} {self.username}>"

    def __eq__(self, other):
        return (
            isinstance(other, AuthUser)
            and self.id == other.id
            and self.username == other.username
            and self.password == other.password
            and self.superuser == other.superuser
        )
