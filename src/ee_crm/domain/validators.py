"""Validators classes for enforcing domain-level data integrity.

Classes
    BaseValidator           # Generic validators.
    AuthUserValidator       # AuthUser Specific checks.
    CollaboratorValidator   # Collaborator Specific checks.
    ClientValidator         # Client Specific checks.
    ContractValidator       # Contract Specific checks.
    EventValidator          # Event Specific checks.

Each validator sets a 'cls_error' to its own 'NameValidatorError'
subclass. Errors are raised as ValidatorError subclasses.
"""
from abc import ABC
from datetime import datetime
from re import search, match

from ee_crm.exceptions import AuthUserValidatorError, \
    CollaboratorValidatorError, ContractValidatorError, ClientValidatorError, \
    EventValidatorError


class BaseValidator(ABC):
    """Abstract base class for validators.

    Attributes:
        cls_error (None|Exception): Specific exception implemented by
            children.
    """
    cls_error = None

    @classmethod
    def _raise(cls, error, tips):
        """Raise an exception according to the error.

        Args:
            error (str): Error message, for devs debug.
            tips (str): Error tips. Used to add additional information.

        Raises:
            Exception: Specific exception raised by children.
        """
        err = cls.cls_error(error)
        err.tips = (f"The provided data couldn't be validated before being "
                    f"written in the database. {tips}")
        raise err

    @staticmethod
    def is_too_long(string, length=255):
        """Check if string is too long.

        Args:
            string (str): String to check.
            length (int): Length of string to check.

        Return:
              bool: True if string is too long.
        """
        return len(string) > length

    @classmethod
    def validate_str(cls, string):
        """Check if string respect several conditions.

        Args:
            string (str): String to check.

        Raises:
            Exception: Specific exception raised by children, if is not
                a str, or is too long.
        """
        if not isinstance(string, str):
            err = "Wrong type must be a string"
            tips = f"The text {string} isn't valid."
            cls._raise(err, tips)
        if cls.is_too_long(string):
            tips = (f"The text \"{string}\" is too long, it must not "
                    f"exceed 255 characters.")
            err = "String too long"
            cls._raise(err, tips)

    @classmethod
    def validate_email(cls, email):
        """Check if email respect several conditions.

        Args:
            email (str): Email to check.

        Raises:
            Exception: Specific exception raised by children, if is not
                a str, is too long or does not contain one sign '@'.

        """
        cls.validate_str(email)

        regex = r'^[^@]+@[^@]+$'
        if not match(regex, email):
            err = "Email format invalid"
            tips = (f'The provided email "{email}" isn\'t valid. it must at '
                    f'least contains a sign "@".')
            cls._raise(err, tips)

    @classmethod
    def validate_phone_number(cls, phone_number):
        """Check if phone number respect several conditions.

        Args:
            phone_number (str): Phone number to check.

        Raises:
            Exception: Specific exception raised by children, if is not
                a str, or is too long (more than 20 characters).
        """
        if not isinstance(phone_number, str):
            err = "Phone number must be a string"
            tips = f"The phone number \"{phone_number}\" isn't valid."
            cls._raise(err, tips)
        if cls.is_too_long(phone_number, length=20):
            err = "Phone number too long"
            tips = (f"The phone number \"{phone_number}\" is too long, it "
                    f"must not exceed 20 characters.")
            cls._raise(err, tips)

    @classmethod
    def validate_positive_int(cls, k_id):
        """Check if the value is a positive integer.

        Args:
            k_id (int): Key ID, or primary key.

        Raises:
            Exception: Specific exception raised by children, if is not
                an int, or a negative integer.

        """
        if not isinstance(k_id, int) or k_id <= 0:
            err = "Invalid id, must be a positive integer"
            tips = f"The pk \"{k_id}\" isn't valid."
            cls._raise(err, tips)


class AuthUserValidator(BaseValidator):
    """Class for AuthUser Validators.

    Attributes:
        cls_error (AuthUserValidatorError): Class specific exception.
    """
    cls_error = AuthUserValidatorError

    @classmethod
    def validate_username(cls, username):
        """Check if username respect several conditions.

        Args:
            username (str): Username to check.

        Raises:
            AuthUserValidatorError: if username is not a str, is too
                long, or too short.
        """
        cls.validate_str(username)
        if len(username) <= 3:
            err = "Username too short"
            tips = (f"The username \"{username}\" isn't valid. It must at "
                    f"least be longer than 4 characters.")
            cls._raise(err, tips)

    @classmethod
    def validate_password(cls, plain_password):
        """Check if plain_password respect several conditions.

        Args:
            plain_password (str): Password (Not hashed) to check.

        Raises:
            AuthUserValidatorError: if plain_password is not a str,
                is too long, is too short, doesn't contain at least one
                of each [number, uppercase, lowercase].
        """
        if not isinstance(plain_password, str):
            err = "Password must be a string"
            tips = f"The password \"*******\" isn't valid."
            cls._raise(err, tips)
        if cls.is_too_long(plain_password):
            err = "Password too long"
            tips = (f"The password \"*******\" is too long, it must not "
                    f"exceed 255 characters.")
            cls._raise(err, tips)
        if not (
                len(plain_password) >= 8 and
                search(r"[A-Z]", plain_password) and
                search(r"[a-z]", plain_password) and
                search(r"\d", plain_password)
        ):
            err = "password too weak"
            tips = (f"The password \"*******\" is too weak, it must meet the"
                    f"following requirements : at least 8 characters, at "
                    f"least 1 number, at least one uppercase, at least one "
                    f"lowercase.")
            cls._raise(err, tips)


class CollaboratorValidator(BaseValidator):
    """Class for Collaborator Validators.

    Attributes:
        cls_error (CollaboratorValidatorError): Class specific exception.
    """
    cls_error = CollaboratorValidatorError

    @classmethod
    def validate_role(cls, role):
        """
        TODO: delete and us Role.sanitizer() in domain's model
        Check if role respect several conditions.

        Args:
            role (int): Role to check.

        Raises:
            CollaboratorValidatorError: if role is not in the set of
                accepted roles.
        """
        if role not in {1, 2, 3, 4, 5}:
            err = "Invalid role"
            tips = (f'The role "{role}" isn\'t valid. It must be one of the'
                    f'following : "DEACTIVATED", "ADMIN", "MANAGEMENT", '
                    f'"SALES", "SUPPORT."')
            cls._raise(err, tips)


class ClientValidator(BaseValidator):
    """Class for Client Validators.

    Attributes:
        cls_error (ClientValidatorError): Class specific exception.
    """
    cls_error = ClientValidatorError


class ContractValidator(BaseValidator):
    """Class for Contract Validators.

    Attributes:
        cls_error (ContractValidatorError): Class specific exception.
    """
    cls_error = ContractValidatorError

    @classmethod
    def validate_price(cls, price):
        """Check if price respect several conditions.

        Args:
            price (float|int): Price to check.

        Raises:
            ContractValidatorError: if price is not a float or an int,
                or is negative.
        """
        if not isinstance(price, (float, int)):
            err = "Invalid price type"
            tips = f"The price \"{price}\" isn't valid. It must be an numeric."
            cls._raise(err, tips)
        if price < 0:
            err = "Invalid price value, must be positive"
            tips = (f"The price \"{price}\" isn't valid. It must be a "
                    f"positive number.")
            cls._raise(err, tips)


class EventValidator(BaseValidator):
    """Class for Event Validators.

    Attributes:
        cls_error (EventValidatorError): Class specific exception.
    """
    cls_error = EventValidatorError

    @classmethod
    def validate_date(cls, date):
        """Check if date respect several conditions.

        Args:
            date (datetime): Date to check.

        Raises:
            EventValidatorError: if date is not a datetime.
        """
        if not isinstance(date, datetime):
            err = "Invalid date type"
            tips = (f'The date "{date}" isn\'t valid. It must at '
                    f'least contains the year, month and day following this'
                    f'pattern : "YYYY-MM-DD". '
                    f'It can also accept hours, minutes and seconds with '
                    f'the following pattern : '
                    f'"YYYY-MM-DD HH:MM:SS".')
            cls._raise(err, tips)

    @classmethod
    def validate_attendee(cls, attendee):
        """Check if attendee respect several conditions.

        Args:
            attendee (int): Number of attendee to check.

        Raises:
            EventValidatorError: if attendee is not an int, or is
                negative.
        """
        if not isinstance(attendee, int) or attendee <= 0:
            err = "Invalid attendee value, must be a positive integer"
            tips = ("The attendee \"{attendee}\" isn't valid. You can only "
                    "use a positive whole digit as the number of attendee.")
            cls._raise(err, tips)

    @classmethod
    def validate_notes(cls, notes):
        """Check if notes respect several conditions.

        Args:
            notes (str): Notes to check.

        Raises:
            EventValidatorError: if notes is not a str, or is too long.
        """
        if not isinstance(notes, str):
            err = "Invalid notes type, must be a string"
            tips = f"The notes \"{notes}\" isn\'t valid."
            cls._raise(err, tips)
        if len(notes) >= 9999:
            err = "Notes too long, must be less than 9999 characters"
            tips = ("The added notes are too long, it mustn't exceed 9999 "
                    "characters. Notes : \"{notes}\".")
            cls._raise(err, tips)
