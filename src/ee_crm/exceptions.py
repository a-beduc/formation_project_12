"""Custom exception hierarchy for the ee_crm project.
Groups of errors by layer, DomainError, ServiceError, ControllerError
all inherits from CRMException.

CRMException introduce attreibutes:
    'threat' (str)  # Logging and UI severity
    'level' (str)   # "domain"|"service"|"controller"
    'tips' (str)    # Short message to help user.

CRMException
├── DomainError
│   ├── AuthUserDomainError
│   ├── CollaboratorDomainError
│   ├── ClientDomainError
│   ├── ContractDomainError
│   ├── EventDomainError
│   └── ValidatorError
│       ├── AuthUserValidatorError
│       ├── CollaboratorValidatorError
│       ├── ClientValidatorError
│       ├── ContractValidatorError
│       └── EventValidatorError
├── ServiceError
│   ├── AuthenticationError
│   ├── TokenError
│   │   ├── BadToken
│   │   ├── ExpiredToken
│   │   └── NoToken
│   ├── ClientServiceError
│   ├── CollaboratorServiceError
│   ├── ContractServiceError
│   ├── EventServiceError
│   └── UserServiceError
└── ControllerError
    ├── InputError
    ├── AuthorizationDenied
    └── BaseManagerError
        ├── ClientManagerError
        ├── CollaboratorManagerError
        ├── ContractManagerError
        ├── EventManagerError
        └── UserManagerError
"""


class CRMException(Exception):
    """Base exception for ee_crm.

    Attributes
        threat (str): Either "error" or "warning".
        level (str): Sub layer where the exception was raised.
        tips (str): Short message to help user.
    """
    threat = "error"
    level = None
    tips = ''


class DomainError(CRMException):
    """Base exception for the domain-layer errors."""
    level = "domain"


class AuthUserDomainError(DomainError):
    """Domain error for the AuthUser model."""
    pass


class CollaboratorDomainError(DomainError):
    """Domain error for the Collaborator model."""
    pass


class ClientDomainError(DomainError):
    """Domain error for the Client model."""
    pass


class ContractDomainError(DomainError):
    """Domain error for the Contract model."""
    pass


class EventDomainError(DomainError):
    """Domain error for the Event model."""
    pass


class ValidatorError(DomainError):
    """Domain base error for the validator helpers."""
    pass


class AuthUserValidatorError(ValidatorError):
    """Domain validator error for the AuthUser model."""
    pass


class CollaboratorValidatorError(ValidatorError):
    """Domain validator error for the Collaborator model."""
    pass


class ClientValidatorError(ValidatorError):
    """Domain validator error for the Client model."""
    pass


class ContractValidatorError(ValidatorError):
    """Domain validator error for the Contract model."""
    pass


class EventValidatorError(ValidatorError):
    """Domain validator error for the Event model."""
    pass


class ServiceError(CRMException):
    """Base exception for the service-layer errors."""
    level = "service"


class AuthenticationError(ServiceError):
    """Exception for the authentication service errors."""
    pass


class TokenError(ServiceError):
    """Base Exception for the token service errors."""
    pass


class BadToken(TokenError):
    """Exception where token integrity is not respected."""
    pass


class ExpiredToken(TokenError):
    """Exception where token lifetime expired."""
    pass


class NoToken(TokenError):
    """Exception where token was not found."""
    pass


class ClientServiceError(ServiceError):
    """Service exception for the client service errors."""
    pass


class CollaboratorServiceError(ServiceError):
    """Service exception for the collaborator service errors."""
    pass


class ContractServiceError(ServiceError):
    """Service exception for the contract service errors."""
    pass


class EventServiceError(ServiceError):
    """Service exception for the event service errors."""
    pass


class UserServiceError(ServiceError):
    """Service exception for the user service errors."""
    pass


class ControllerError(CRMException):
    """Base exception for the controller errors."""
    level = "controller"


class InputError(ControllerError):
    """Controller exception for the input errors."""
    threat = "warning"
    pass


class AuthorizationDenied(ControllerError):
    """Controller exception for the authorization denied errors."""
    pass


class BaseManagerError(ControllerError):
    """Controller base exception for the resource manager errors."""
    pass


class ClientManagerError(BaseManagerError):
    """Controller exception for the client manager errors."""
    pass


class CollaboratorManagerError(BaseManagerError):
    """Controller exception for the collaborator manager errors."""
    pass


class ContractManagerError(BaseManagerError):
    """Controller exception for the contract manager errors."""
    pass


class EventManagerError(BaseManagerError):
    """Controller exception for the event manager errors."""
    pass


class UserManagerError(BaseManagerError):
    """Controller exception for the user manager errors."""
    pass
