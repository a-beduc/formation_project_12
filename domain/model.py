from re import search
from argon2 import PasswordHasher, exceptions

from dataclasses import dataclass, field, fields
from datetime import datetime


class DomainError(Exception):
    pass


class AuthUserError(DomainError):
    pass


@dataclass(kw_only=True)
class AuthUser:
    id: int | None = field(init=False, default=None)
    username: str
    password: str

    @staticmethod
    def validate_username(username):
        if len(username) <= 3:
            raise AuthUserError("username too short")

    @staticmethod
    def validate_password(plain_password):
        if not (
                len(plain_password) >= 8 and
                search(r"[A-Z]", plain_password) and
                search(r"[a-z]", plain_password) and
                search(r"\d", plain_password)
        ):
            raise AuthUserError(
                "password too weak, need 8 char, 1 number, 1 upper, 1 lower"
            )

    @staticmethod
    def hash_plain_password(plain_password):
        ph = PasswordHasher()
        return ph.hash(plain_password)

    def set_password(self, plain_password):
        self.validate_password(plain_password)
        self.password = self.hash_plain_password(plain_password)

    def verify_password(self, plain_password):
        ph = PasswordHasher()
        try:
            ph.verify(self.password, plain_password)
        except exceptions.VerifyMismatchError:
            raise AuthUserError(f"Password mismatch")

    @classmethod
    def build_user(cls, username, plain_password):
        hash_password = cls.hash_plain_password(plain_password)
        return cls(
            username=username,
            password=hash_password
        )


@dataclass(kw_only=True)
class Role:
    id: int | None = field(init=False, default=None)
    role: str


@dataclass(kw_only=True)
class Collaborator:
    id: int | None = field(init=False, default=None)
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    role_id: int = 1
    user_id: int

    @staticmethod
    def get_updatable_fields():
        return {"last_name", "first_name", "email", "phone_number", "role_id"}


@dataclass(kw_only=True)
class Client:
    id: int | None = field(init=False, default=None)
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    company: str | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    salesman_id: int


@dataclass(kw_only=True)
class Contract:
    id: int | None = field(init=False, default=None)
    total_amount: float
    paid_amount: float = 0.0
    created_at: datetime = datetime.now()
    signed: bool = False
    client_id: int

    def calculate_due_amount(self):
        return round(self.total_amount - self.paid_amount, 2)


@dataclass(kw_only=True)
class Event:
    id: int | None = field(init=False, default=None)
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    attendee: int | None = None
    notes: str | None = None
    supporter_id: int | None = None
    contract_id: int
