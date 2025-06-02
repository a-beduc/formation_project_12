from abc import ABC
from re import search, match
from datetime import datetime


class ValidatorError(Exception):
    pass


class AuthUserValidatorError(ValidatorError):
    pass


class CollaboratorValidatorError(ValidatorError):
    pass


class ClientValidatorError(ValidatorError):
    pass


class ContractValidatorError(ValidatorError):
    pass


class EventValidatorError(ValidatorError):
    pass


class BaseValidator(ABC):
    cls_error = None

    @classmethod
    def _raise(cls, error):
        raise cls.cls_error(error)

    @staticmethod
    def is_too_long(string, length=255):
        return len(string) > length

    @classmethod
    def validate_str(cls, string):
        if not isinstance(string, str):
            cls._raise(f"Wrong type must be a string")
        if cls.is_too_long(string):
            cls._raise(f"String too long")

    @classmethod
    def validate_email(cls, email):
        cls.validate_str(email)

        regex = r'^[^@]+@[^@]+$'
        if not match(regex, email):
            cls._raise("Email format invalid")

    @classmethod
    def validate_phone_number(cls, phone_number):
        if not isinstance(phone_number, str):
            cls._raise("Phone number must be a string")
        if cls.is_too_long(phone_number, length=20):
            cls._raise("Phone number too long")

    @classmethod
    def validate_id(cls, k_id):
        if not isinstance(k_id, int) or k_id <= 0:
            cls._raise("Invalid id, must be a positive integer")


class AuthUserValidator(BaseValidator):
    cls_error = AuthUserValidatorError

    @classmethod
    def validate_username(cls, username):
        cls.validate_str(username)
        if len(username) <= 3:
            cls._raise("Username too short")

    @classmethod
    def validate_password(cls, plain_password):
        if not isinstance(plain_password, str):
            cls._raise("Password must be a string")
        if cls.is_too_long(plain_password):
            cls._raise("Password too long")
        if not (
                len(plain_password) >= 8 and
                search(r"[A-Z]", plain_password) and
                search(r"[a-z]", plain_password) and
                search(r"\d", plain_password)
        ):
            cls._raise("password too weak, need at least 8 char, 1 number, "
                       "1 upper, 1 lower")


class CollaboratorValidator(BaseValidator):
    cls_error = CollaboratorValidatorError

    @classmethod
    def validate_role(cls, role, role_types):
        if role not in role_types:
            cls._raise("Invalid role")


class ClientValidator(BaseValidator):
    cls_error = ClientValidatorError


class ContractValidator(BaseValidator):
    cls_error = ContractValidatorError

    @classmethod
    def validate_price(cls, price):
        if not isinstance(price, (float, int)):
            cls._raise("Invalid price type")
        if price < 0:
            cls._raise("Invalid price value, must be positive")


class EventValidator(BaseValidator):
    cls_error = EventValidatorError

    @classmethod
    def validate_date(cls, date):
        if not isinstance(date, datetime):
            cls._raise("Invalid date type")

    @classmethod
    def validate_attendee(cls, attendee):
        if not isinstance(attendee, int) or attendee <= 0:
            cls._raise("Invalid attendee value, "
                                "must be a positive integer")

    @classmethod
    def validate_notes(cls, notes):
        if not isinstance(notes, str):
            cls._raise("Invalid notes type, must be a string")
        if len(notes) >= 9999:
            cls._raise("Notes too long, must be less than 9999 characters")
