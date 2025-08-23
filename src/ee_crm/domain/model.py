"""Domain models and business rules for the CRM.

Classes
    AuthUser        # Entity, dataclass
    Role            # Enum
    Collaborator    # Entity, dataclass
    Client          # Entity, dataclass
    Contract        # Entity, dataclass
    Event           # Entity, dataclass

Each entity implements:
* Validation at construction through a 'builder()' factory method.
* Pure domain methods.
* Private attributes to avoid careless manipulation of data.

Errors are raised up as DomainError subclasses.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from math import trunc

from argon2 import PasswordHasher, exceptions

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
    """User data for authentication purposes.

    Attributes:
        id (int | None): Primary key set by the persistence layer.
        _username (str): User's username.
        _password (str): User's hashed password.
    """
    id: int | None = field(init=False, default=None)
    _username: str
    _password: str

    # Hacky way to link public properties to private properties
    _private_aliases = {"username": "_username"}

    @property
    def username(self):
        """User's username public property.

        Returns:
            str: User's username.
        """
        return self._username

    @username.setter
    def username(self, username):
        """User's username setter.

        Args:
            username (str): User's username.

        Raises:
            AuthUserValidatorError: If the username doesn't pass
                validator func.
        """
        AuthVal.validate_username(username)
        self._username = username

    @staticmethod
    def hash_plain_password(plain_password):
        """Hash a plain-text password.

        Args:
            plain_password (str): Plain-text password.

        Returns:
            str: hashed password.
        """
        ph = PasswordHasher()
        return ph.hash(plain_password)

    @staticmethod
    def filterable_fields():
        """Set of keywords to get the accepted public filters fields.

        Returns:
            set[str]: Set of keywords.
        """
        return {'id', 'username'}

    def set_password(self, plain_password):
        """Public method to set a password.

        Args:
            plain_password (str): Plain-text password.

        Raises:
            AuthUserValidatorError: If validation fails.
        """
        AuthVal.validate_password(plain_password)
        self._password = self.hash_plain_password(plain_password)

    def verify_password(self, plain_password):
        """Verify given plain_password hashed is the same as user's
        _password.

        Args:
            plain_password (str): Password to verify.

        Raises:
            AuthUserDomainError: Raised if user's password does not
                match
        """
        ph = PasswordHasher()
        try:
            ph.verify(self._password, plain_password)
        except exceptions.VerifyMismatchError:
            err = AuthUserDomainError("Password mismatch")
            err.tips = ("The provided password doesn't match with the password"
                        " saved in database for this user. Verify your input "
                        "and try again.")
            raise err

    @classmethod
    def builder(cls, username, plain_password):
        """Method to safely build a new instance of AuthUser.

        Args:
            username (str): User's username.
            plain_password (str): User's password.

        Returns:
            AuthUser: New AuthUser instance.

        Raises:
            AuthUserValidatorError: If validation fails.
        """
        AuthVal.validate_username(username)
        AuthVal.validate_password(plain_password)
        hash_password = cls.hash_plain_password(plain_password)
        return cls(
            _username=username,
            _password=hash_password
        )


class Role(IntEnum):
    """Company's role assigned to a collaborator.

    Values:
        DEACTIVATED (1): Account disabled.
        ADMIN (2): Admin account (not implemented yet).
        MANAGEMENT (3): Management account.
        SALES (4): Sales account.
        SUPPORT (5): Support account.
    """
    DEACTIVATED = 1
    ADMIN = 2
    MANAGEMENT = 3
    SALES = 4
    SUPPORT = 5

    @classmethod
    def sanitizer(cls, value):
        """Transform input into the corresponding Role.

        Args:
            value (int | str | Role): Possible role input.

        Returns:
            Role: The corresponding Role.

        Raises:
            CollaboratorDomainError: If the input isn't corresponding to
                a valid role.
        """
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
    """Application data and methods for collaborators.

    Attributes:
        id (int | None): Primary key set by the persistence layer.
        last_name (str | None): Collaborator's last name.
        first_name (str | None): Collaborator's first name.
        email (str | None): Collaborator's email address.
        phone_number (str | None): Collaborator's phone number.
        _role_id (Role): Collaborator's role, stored as int in DB.
        _user_id (int): ID of AuthUser whose linked to this collaborator.
    """
    id: int | None = field(init=False, default=None)
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    _role_id: Role = Role.DEACTIVATED
    _user_id: int

    # Hacky way to link public properties to private properties
    _private_aliases = {"user_id": "_user_id",
                        "role": "_role_id"}

    @property
    def user_id(self):
        """ID of Collaborator's AuthUser, public property.

        Returns:
            int: AuthUser's id.
        """
        return self._user_id

    @property
    def role(self):
        """Role of Collaborator, public property.

        Returns:
            Role: Collaborator's role.
        """
        return Role(self._role_id)

    @role.setter
    def role(self, value):
        """Setter of Collaborator's role. Verify input before setting it.

        Args:
            value (Role): Collaborator's role.

        Raises:
            CollaboratorDomainError: If the input can't be converted to
                a valid role.
        """
        self._role_id = Role.sanitizer(value)

    @staticmethod
    def updatable_fields():
        """Set of keywords to get the accepted public updatable fields.

        Returns:
            set[str]: Set of keywords.
        """
        return {"last_name", "first_name", "email", "phone_number"}

    @staticmethod
    def filterable_fields():
        """Set of keywords to get the accepted public filters fields.

        Returns:
            set[str]: Set of keywords.
        """
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
        """Method to safely build a new instance of Collaborator.

        Args:
            last_name (str): Collaborator's last name.
            first_name (str): Collaborator's first name.
            email (str): Collaborator's email address.
            phone_number (str): Collaborator's phone number.
            role (Role): Collaborator's role.
            user_id (int): ID of AuthUser who is linked to this collaborator.

        Returns:
            Collaborator: New Collaborator instance.

        Raises:
            CollaboratorValidatorError: If any validation fails.
        """
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
    """Application data and domain methods for clients entities.

    Attributes:
        id (int | None): Primary key set by the persistence layer.
        last_name (str | None): Client's last name.
        first_name (str | None): Client's first name.
        email (str | None): Client's email address.
        phone_number (str | None): Client's phone number.
        company (str | None): Client's company name.
        _created_at (datetime): Creation timestamp.
        _updated_at (datetime): Modification timestamp.
        _salesman_id (int): ID of Collaborator who is linked to this client.
    """
    id: int | None = field(init=False, default=None)
    last_name: str | None = None
    first_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    company: str | None = None
    _created_at: datetime = datetime.now()
    _updated_at: datetime = datetime.now()
    _salesman_id: int | None = None

    # Hacky way to link public properties to private properties
    _private_aliases = {"created_at": "_created_at",
                        "updated_at": "_updated_at",
                        "salesman_id": "_salesman_id", }

    @property
    def created_at(self):
        """Creation timestamp public property.

        Returns:
            datetime: Creation timestamp.
        """
        return self._created_at

    @property
    def updated_at(self):
        """Modification timestamp public property.

        Returns:
            datetime: Modification timestamp.
        """
        return self._updated_at

    @property
    def salesman_id(self):
        """ID of Collaborator who is linked to this client,
         public property.

        Returns:
            int: ID of Collaborator who is linked to this client.
        """
        return self._salesman_id

    def __setattr__(self, name, value):
        """Change 'Modification timestamp' whenever an attribute is set.
        Except for self._updated_at to avoid recursion.

        Args:
            name (str): Attribute name.
            value (Any): Attribute value.
        """
        super().__setattr__(name, value)
        if name != "_updated_at":
            super().__setattr__("_updated_at", datetime.now())

    @staticmethod
    def updatable_fields():
        """Set of keywords to get the accepted public updatable fields.

        Returns:
            set[str]: Set of keywords.
        """
        return {"last_name", "first_name", "email", "phone_number", "company"}

    @staticmethod
    def filterable_fields():
        """Set of keywords to get the accepted public filters fields.

        Returns:
            set[str]: Set of keywords.
        """
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
        """Method to safely build a new instance of Client.

        Args:
            last_name (str): Client's last name.
            first_name (str): Client's first name.
            email (str): Client's email address.
            phone_number (str): Client's phone number.
            company (str): Client's company name.
            salesman_id (int): ID of Collaborator who is linked to this
            client.

        Returns:
            Client: New Client instance.

        Raises:
            ClientValidatorError: If any validation fails.
        """
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
    """Application data and domain methods for contracts entities.
    Mostly use designated methods to interacts with its data.

    Attributes:
        id (int | None): Primary key set by the persistence layer.
        _total_amount (float): Total amount of the contract.
        _paid_amount (float): Paid amount of the contract.
        created_at (datetime): Creation timestamp.
        _signed (bool): True if contract is signed.
        _client_id (int): ID of Client who is linked to this contract.
    """
    id: int | None = field(init=False, default=None)
    _total_amount: float | None = 0.00
    _paid_amount: float | None = 0.00
    created_at: datetime = datetime.now()
    _signed: bool | None = False
    _client_id: int | None = None

    # Hacky way to link public properties to private properties
    _private_aliases = {"total_amount": "_total_amount",
                        "paid_amount": "_paid_amount",
                        "signed": "_signed",
                        "client_id": "_client_id"}

    @property
    def total_amount(self):
        """Total amount of the contract, public property.

        Returns:
            float: Total amount of the contract.
        """
        return self._total_amount

    @total_amount.setter
    def total_amount(self, new_total):
        """Set total amount of the contract, public property.

        Args:
            new_total (float | int | str): Total amount of the contract.

        Raises:
            ContractValidatorError: If validation fails.
        """
        self.change_total_amount(new_total)

    @property
    def paid_amount(self):
        """Current paid amount of the contract, public property.

        Returns:
            float: Current paid amount of the contract.
        """
        return self._paid_amount

    @property
    def signed(self):
        """Contract signed status, public property.

        Returns:
            bool: True if contract is signed.
        """
        return self._signed

    @property
    def client_id(self):
        """ID of Client who is linked to this contract, public property.

        Returns:
            int: ID of Client who is linked to this contract.
        """
        return self._client_id

    def sign(self):
        """Sign contract."""
        self._signed = True

    def change_total_amount(self, new_total):
        """Change total amount of the contract.

        Args:
            new_total (float | int | str): Total amount of the contract.

        Raises:
            ContractValidatorError: If amount validation fails.
            ContractDomainError: If Contract already signed.
        """
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
        """Register a payment.

        Args:
            amount (float | int | str): Amount to be registered.

        Raises:
            ContractDomainError: If Contract is not signed, the payment
                amount is not positive, the payment exceed the due
                amount.
            ContractValidatorError: If amount validation fails.
        """
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
        """Calculate due amount.

        Returns:
            float: Due amount.
        """
        return round(self._total_amount - self._paid_amount, 2)

    def updatable_fields(self):
        """Set of keywords to get the accepted public updatable fields.

        Returns:
            set[str]: Set of keywords.
        """
        if self._signed:
            return {"paid_amount"}
        return {"total_amount", "paid_amount", "signed"}

    @staticmethod
    def filterable_fields():
        """Set of keywords to get the accepted public filters fields.

        Returns:
            set[str]: Set of keywords.
        """
        return {"id", "total_amount", "paid_amount", "created_at", "signed",
                "client_id"}

    @classmethod
    def builder(cls, total_amount=None, client_id=None):
        """Method to safely build a new instance of Contract.
        Normalize total amount, trunc price to the 2nd digit.

        Args:
            total_amount (float|int|str): Total amount of the contract.
            client_id (int): ID of Client who is linked to this contract.

        Returns:
            Contract: New Contract instance.

        Raises:
            ContractDomainError: If no client's id provided.
            ContractValidatorError: If any validation fails.
        """
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
    """Application data and domain methods for event entities.

    Attributes:
        id (int | None): Primary key set by the persistence layer.
        title (str): Title of the event.
        start_time (datetime): Start time of the event.
        end_time (datetime): End time of the event.
        location (str): Location of the event.
        attendee (int): Number of attendees in the event.
        notes (str): Notes about the event, limited at 9999 characters.
        supporter_id (int): ID of Collaborator who is the supporter of
            the event.
        _contract_id (int): Contract ID of the event.
    """
    id: int | None = field(init=False, default=None)
    title: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    attendee: int | None = None
    notes: str | None = None
    supporter_id: int | None = None
    _contract_id: int | None = None

    # Hacky way to link public properties to private properties
    _private_aliases = {"contract_id": "_contract_id"}

    @property
    def contract_id(self):
        """Contract ID of the event, public property.

        Returns:
            int: Contract ID of the event.
        """
        return self._contract_id

    @staticmethod
    def updatable_fields():
        """Set of keywords to get the accepted public updatable fields.

        Returns:
            set[str]: Set of keywords.
        """
        return {"title", "start_time", "end_time", "location", "attendee",
                "notes"}

    @staticmethod
    def filterable_fields():
        """Set of keywords to get the accepted public filters fields.

        Returns:
            set[str]: Set of keywords.
        """
        return {"id", "title", "start_time", "end_time", "location",
                "attendee", "notes", "supporter_id", "contract_id"}

    @classmethod
    def builder(cls,
                title=None,
                start_time=None,
                end_time=None,
                location=None,
                attendee=None,
                notes=None,
                contract_id=None):
        """Method to safely build a new instance of Event.
        Normalize total amount, trunc price to the 2nd digit.

        Args:
            title (str): Title of the event.
            start_time (datetime): Start time of the event.
            end_time (datetime): End time of the event.
            location (str): Location of the event.
            attendee (int): Number of attendees in the event.
            notes (str): Notes about the event, limited at 9999 characters.
            contract_id (int): Contract ID of the event.

        Returns:
            Event: New Event instance.

        Raises:
            EventDomainError: If no contract's id provided.
            EventValidatorError: If any validation fails.
        """
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
