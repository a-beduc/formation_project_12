from abc import ABC
from datetime import datetime
from re import search, match

from ee_crm.exceptions import AuthUserValidatorError, \
    CollaboratorValidatorError, ContractValidatorError, ClientValidatorError, \
    EventValidatorError


class BaseValidator(ABC):
    cls_error = None

    @classmethod
    def _raise(cls, error, tips):
        err = cls.cls_error(error)
        err.tips = (f"The provided data couldn't be validated before being "
                    f"written in the database. {tips}")
        raise err

    @staticmethod
    def is_too_long(string, length=255):
        return len(string) > length

    @classmethod
    def validate_str(cls, string):
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
        cls.validate_str(email)

        regex = r'^[^@]+@[^@]+$'
        if not match(regex, email):
            err = "Email format invalid"
            tips = (f'The provided email "{email}" isn\'t valid. it must at '
                    f'least contains a sign "@".')
            cls._raise(err, tips)

    @classmethod
    def validate_phone_number(cls, phone_number):
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
        if not isinstance(k_id, int) or k_id <= 0:
            err = "Invalid id, must be a positive integer"
            tips = f"The pk \"{k_id}\" isn't valid."
            cls._raise(err, tips)


class AuthUserValidator(BaseValidator):
    cls_error = AuthUserValidatorError

    @classmethod
    def validate_username(cls, username):
        cls.validate_str(username)
        if len(username) <= 3:
            err = "Username too short"
            tips = (f"The username \"{username}\" isn't valid. It must at "
                    f"least be longer than 4 characters.")
            cls._raise(err, tips)

    @classmethod
    def validate_password(cls, plain_password):
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
    cls_error = CollaboratorValidatorError

    @classmethod
    def validate_role(cls, role):
        if role not in {1, 2, 3, 4, 5}:
            err = "Invalid role"
            tips = (f'The role "{role}" isn\'t valid. It must be one of the'
                    f'following : "DEACTIVATED", "ADMIN", "MANAGEMENT", '
                    f'"SALES", "SUPPORT."')
            cls._raise(err, tips)


class ClientValidator(BaseValidator):
    cls_error = ClientValidatorError


class ContractValidator(BaseValidator):
    cls_error = ContractValidatorError

    @classmethod
    def validate_price(cls, price):
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
    cls_error = EventValidatorError

    @classmethod
    def validate_date(cls, date):
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
        if not isinstance(attendee, int) or attendee <= 0:
            err = "Invalid attendee value, must be a positive integer"
            tips = ("The attendee \"{attendee}\" isn't valid. You can only "
                    "use a positive whole digit as the number of attendee.")
            cls._raise(err, tips)

    @classmethod
    def validate_notes(cls, notes):
        if not isinstance(notes, str):
            err = "Invalid notes type, must be a string"
            tips = f"The notes \"{notes}\" isn\'t valid."
            cls._raise(err, tips)
        if len(notes) >= 9999:
            err = "Notes too long, must be less than 9999 characters"
            tips = ("The added notes are too long, it mustn't exceed 9999 "
                    "characters. Notes : \"{notes}\".")
            cls._raise(err, tips)
