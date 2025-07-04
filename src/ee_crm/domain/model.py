from argon2 import PasswordHasher, exceptions
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from math import trunc

from ee_crm.domain.validators import (
    AuthUserValidator as AuthVal,
    CollaboratorValidator as ColVal,
    ClientValidator as CliVal,
    ContractValidator as ConVal,
    EventValidator as EveVal
)
from ee_crm.exceptions import AuthUserDomainError, CollaboratorDomainError, \
    ClientDomainError, ContractDomainError, EventDomainError


@dataclass(kw_only=True)
class AuthUser:
    id: int | None = field(init=False, default=None)
    _username: str
    _password: str

    _private_aliases = {"username": "_username"}

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        AuthVal.validate_username(username)
        self._username = username

    @staticmethod
    def hash_plain_password(plain_password):
        ph = PasswordHasher()
        return ph.hash(plain_password)

    @staticmethod
    def filterable_fields():
        return {'id', 'username'}

    def set_password(self, plain_password):
        AuthVal.validate_password(plain_password)
        self._password = self.hash_plain_password(plain_password)

    def verify_password(self, plain_password):
        ph = PasswordHasher()
        try:
            ph.verify(self._password, plain_password)
        except exceptions.VerifyMismatchError:
            err = AuthUserDomainError(f"Password mismatch")
            err.tips = ("The provided password doesn't match with the password"
                        " saved in database for this user. Verify your input "
                        "and try again.")
            raise err

    @classmethod
    def builder(cls, username, plain_password):
        AuthVal.validate_username(username)
        AuthVal.validate_password(plain_password)
        hash_password = cls.hash_plain_password(plain_password)
        return cls(
            _username=username,
            _password=hash_password
        )


class Role(IntEnum):
    DEACTIVATED = 1
    ADMIN = 2
    MANAGEMENT = 3
    SALES = 4
    SUPPORT = 5

    @classmethod
    def sanitizer(cls, value):
        if isinstance(value, cls):
            return value

        try:
            return cls(int(value))
        except (ValueError, TypeError):
            pass

        if isinstance(value, str):
            try:
                return cls[value.upper()]
            except KeyError:
                pass

        err = CollaboratorDomainError(f"Invalid role: {value}")
        err.tips = ('Role can be one of '
                    '"DEACTIVATED", "MANAGEMENT", "SALES", "SUPPORT". '
                    'Verify your input and try again')
        raise err


@dataclass(kw_only=True)
class Collaborator:
    id: int | None = field(init=False, default=None)
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    _role_id: Role = Role.DEACTIVATED
    _user_id: int

    _private_aliases = {"user_id": "_user_id",
                        "role": "_role_id"}

    @property
    def user_id(self):
        return self._user_id

    @property
    def role(self):
        return Role(self._role_id)

    @role.setter
    def role(self, value):
        if not isinstance(value, Role):
            err = CollaboratorDomainError(
                "Role must be an instance of RoleType")
            err.tips = ('Role can be one of '
                        '"DEACTIVATED", "MANAGEMENT", "SALES", "SUPPORT". '
                        'Verify your input and try again')
            raise err
        self._role_id = int(value)

    @staticmethod
    def updatable_fields():
        return {"last_name", "first_name", "email", "phone_number"}

    @staticmethod
    def filterable_fields():
        return {'id', "last_name", "first_name", "email", "phone_number",
                "role", 'user_id'}

    @classmethod
    def builder(cls, *,
                last_name=None,
                first_name=None,
                email=None,
                phone_number=None,
                role=Role.DEACTIVATED,
                user_id=None):

        if not user_id:
            err = CollaboratorDomainError("Collaborator must have a linked "
                                          "user")
            err.tips = ('The provided user id is not linked to a user in the '
                        'database, critical error, contact support.')
            raise err

        data = {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone_number": phone_number,
            "role": Role.sanitizer(role),
            "user_id": user_id
        }

        val_map = {
            "last_name": ColVal.validate_str,
            "first_name": ColVal.validate_str,
            "email": ColVal.validate_email,
            "phone_number": ColVal.validate_phone_number,
            "role": ColVal.validate_role,
            "user_id": ColVal.validate_positive_int
        }

        for k, v in data.items():
            if v is not None:
                val_map[k](v)

        return cls(last_name=data["last_name"],
                   first_name=data["first_name"],
                   email=data["email"],
                   phone_number=data["phone_number"],
                   _role_id=data["role"],
                   _user_id=data["user_id"])


@dataclass(kw_only=True)
class Client:
    id: int | None = field(init=False, default=None)
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    company: str | None = None
    _created_at: datetime = datetime.now()
    _updated_at: datetime = datetime.now()
    _salesman_id: int | None = None

    _private_aliases = {"created_at": "_created_at",
                        "updated_at": "_updated_at",
                        "salesman_id": "_salesman_id", }

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    @property
    def salesman_id(self):
        return self._salesman_id

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name != "_updated_at":
            super().__setattr__("_updated_at", datetime.now())

    @staticmethod
    def updatable_fields():
        return {"last_name", "first_name", "email", "phone_number", "company"}

    @staticmethod
    def filterable_fields():
        return {'id', "last_name", "first_name", "email", "phone_number",
                "company", "created_at", "updated_at", "salesman_id"}

    @classmethod
    def builder(cls, *,
                last_name=None,
                first_name=None,
                email=None,
                phone_number=None,
                company=None,
                salesman_id=None):

        if not salesman_id:
            err = ClientDomainError("Client must have a linked salesman")
            err.tips = ("The given salesman_id isn't linked to a collaborator "
                        "with the SALES role.")
            raise err

        data = {
            "last_name": last_name,
            "first_name": first_name,
            "email": email,
            "phone_number": phone_number,
            "company": company,
            "salesman_id": salesman_id
        }

        val_map = {
            "last_name": CliVal.validate_str,
            "first_name": CliVal.validate_str,
            "email": CliVal.validate_email,
            "phone_number": CliVal.validate_phone_number,
            "company": CliVal.validate_str,
            "salesman_id": CliVal.validate_positive_int
        }

        for k, v in data.items():
            if v is not None:
                val_map[k](v)

        return cls(last_name=data["last_name"],
                   first_name=data["first_name"],
                   email=data["email"],
                   phone_number=data["phone_number"],
                   company=data["company"],
                   _salesman_id=data["salesman_id"])


@dataclass(kw_only=True)
class Contract:
    id: int | None = field(init=False, default=None)
    _total_amount: float | None = 0.00
    _paid_amount: float | None = 0.00
    created_at: datetime = datetime.now()
    _signed: bool | None = False
    _client_id: int | None = None

    _private_aliases = {"total_amount": "_total_amount",
                        "paid_amount": "_paid_amount",
                        "signed": "_signed",
                        "client_id": "_client_id"}

    @property
    def total_amount(self):
        return self._total_amount

    @total_amount.setter
    def total_amount(self, new_total):
        self.change_total_amount(new_total)

    @property
    def paid_amount(self):
        return self._paid_amount

    @property
    def signed(self):
        return self._signed

    @property
    def client_id(self):
        return self._client_id

    def sign(self):
        self._signed = True

    def change_total_amount(self, new_total):
        ConVal.validate_price(new_total)
        validated_price = trunc(new_total * 100) / 100
        if self._signed:
            err = ContractDomainError("Total amount cannot be changed for "
                                      "signed contract.")
            err.tips = ("You cannot change the total amount of a contract "
                        "after it has been signed. You must ask for a new "
                        "contract to be made to modify the total amount.")
            raise err
        self._total_amount = validated_price

    def register_payment(self, amount):
        if not self._signed:
            err = ContractDomainError("Payment can't be registered before "
                                      "signature.")
            err.tips = ("You must sign the contract before being able to "
                        "register any payment. Beware, once signed the total "
                        "amount to pay for the contract will be frozen.")
            raise err
        if amount <= 0:
            err = ContractDomainError("Payment amount must be positive")
            err.tips = ("You can't register an invalid payment amount. "
                        "Assure that the payment is at least 0.")
            raise err
        if amount > (self._total_amount - self._paid_amount):
            err = ContractDomainError(
                f"Payment : {amount} exceed due. "
                f"Still due : {self.calculate_due_amount()}.")
            err.tips = (f"The provided payment is higher than the due amount. "
                        f"Verify amount and try again, if the payment has "
                        f"already been processed, you must pay back the "
                        f"client the following amount : "
                        f"{amount - self.calculate_due_amount()}.")
            raise err
        ConVal.validate_price(amount)
        validated_price = trunc(amount * 100) / 100
        self._paid_amount += validated_price

    def calculate_due_amount(self):
        return round(self._total_amount - self._paid_amount, 2)

    def updatable_fields(self):
        if self._signed:
            return {"paid_amount"}
        return {"total_amount", "paid_amount", "signed"}

    @staticmethod
    def filterable_fields():
        return {"id", "total_amount", "paid_amount", "created_at", "signed",
                "client_id"}

    @classmethod
    def builder(cls, total_amount=None, client_id=None):
        if not client_id:
            err = ContractDomainError("Contract must have a linked client")
            err.tips = ("The given client_id isn't linked to a client in the "
                        "database, verify your input and try again.")
            raise err

        data = {
            "total_amount": total_amount,
            "client_id": client_id
        }

        val_map = {
            "total_amount": ConVal.validate_price,
            "client_id": ConVal.validate_positive_int
        }

        for k, v in data.items():
            if v is not None:
                val_map[k](v)

        if total_amount is not None:
            data["total_amount"] = trunc(total_amount * 100) / 100
        else:
            data["total_amount"] = 0

        return cls(_total_amount=data["total_amount"],
                   _client_id=data["client_id"])


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
    _contract_id: int | None = None

    _private_aliases = {"contract_id": "_contract_id"}

    @property
    def contract_id(self):
        return self._contract_id

    @staticmethod
    def updatable_fields():
        return {"title", "start_time", "end_time", "location", "attendee",
                "notes"}

    @staticmethod
    def filterable_fields():
        return {"id", "title", "start_time", "end_time", "location",
                "attendee", "notes", "supporter_id", "contract_id"}

    @classmethod
    def builder(cls, title=None, start_time=None, end_time=None, location=None,
                attendee=None, notes=None, contract_id=None):
        if not contract_id:
            err = EventDomainError("Contract must have a linked client")
            err.tips = ("The given contract_id isn't linked to a contract in "
                        "the database, verify your input and try again.")
            raise err

        data = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "attendee": attendee,
            "notes": notes,
            "contract_id": contract_id
        }

        val_map = {
            "title": EveVal.validate_str,
            "start_time": EveVal.validate_date,
            "end_time": EveVal.validate_date,
            "location": EveVal.validate_str,
            "attendee": EveVal.validate_positive_int,
            "notes": EveVal.validate_notes,
            "contract_id": EveVal.validate_positive_int,
        }

        for k, v in data.items():
            if v is not None:
                val_map[k](v)

        return cls(title=data["title"],
                   start_time=data["start_time"],
                   end_time=data["end_time"],
                   location=data["location"],
                   attendee=data["attendee"],
                   notes=data["notes"],
                   _contract_id=data["contract_id"])
