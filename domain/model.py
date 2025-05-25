from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class AuthUser:
    id: int | None = field(init=False, default=None)
    username: str
    password: str


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
