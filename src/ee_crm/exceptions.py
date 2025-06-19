class CRMException(Exception):
    # either "error" or "warning"
    threat = "error"
    level = None
    tips = ''


class DomainError(CRMException):
    level = "domain"


class AuthUserDomainError(DomainError):
    pass


class CollaboratorDomainError(DomainError):
    pass


class ClientDomainError(DomainError):
    pass


class ContractDomainError(DomainError):
    pass


class EventDomainError(DomainError):
    pass


class ValidatorError(DomainError):
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


class ServiceError(CRMException):
    level = "service"


class AuthenticationError(ServiceError):
    pass


class TokenError(ServiceError):
    pass


class BadToken(TokenError):
    pass


class ExpiredToken(TokenError):
    pass


class NoToken(TokenError):
    pass


class ClientServiceError(ServiceError):
    pass


class CollaboratorServiceError(ServiceError):
    pass


class ContractServiceError(ServiceError):
    pass


class EventServiceError(ServiceError):
    pass


class UserServiceError(ServiceError):
    pass


class ControllerError(CRMException):
    level = "controller"


class InputError(ControllerError):
    threat = "warning"
    pass


class AuthorizationDenied(ControllerError):
    pass


class BaseManagerError(ControllerError):
    pass


class ClientManagerError(BaseManagerError):
    pass


class CollaboratorManagerError(BaseManagerError):
    pass


class ContractManagerError(BaseManagerError):
    pass


class EventManagerError(BaseManagerError):
    pass


class UserManagerError(BaseManagerError):
    pass
