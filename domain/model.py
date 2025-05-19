from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class AuthUser:
    id: int | None = field(init=False, default=None)
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
