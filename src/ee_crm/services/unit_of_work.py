"""Unit of work pattern implementation.

The following classes should be used as context manager.

Classes
    AbstractUnitOfWork      # Abstract transaction service
    SqlAlchemyUnitOfWork    # SQLAlchemy implementation

References
    * Architecture Patterns with Python
https://www.cosmicpython.com/book/chapter_06_uow.html
"""
from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ee_crm.adapters import repositories as repo
from ee_crm.config import get_postgres_uri


class AbstractUnitOfWork(ABC):
    """Abstract class for unit of-work implementations.

    Attributes
        users: Repository instance, initiated by subclass.
        collaborators: Repository instance, initiated by subclass.
        clients: Repository instance, initiated by subclass.
        contracts: Repository instance, initiated by subclass.
        events: Repository instance, initiated by subclass.
    """
    users: repo.AbstractRepository
    collaborators: repo.AbstractRepository
    clients: repo.AbstractRepository
    contracts: repo.AbstractRepository
    events: repo.AbstractRepository

    def __enter__(self):
        """Context manager protocol start."""
        return self

    def __exit__(self, *args):
        """Context manager protocol end.
        The non-commited/non-saved transaction are rolled back.
        Rollback implementation depends on subclasses.
        """
        self.rollback()

    def commit(self):
        """Flush and commit pending changes to the data persistence
        system.
        """
        self._commit()

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def _commit(self):
        raise NotImplementedError


# Executed at import time, may be better to add a factory func that yield Sess
DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(get_postgres_uri()),
    autoflush=True,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy implementation for unit of-work, it wires five
    repositories to the session.

    Attributes:
        session_factory (Session): Factory returning a SQLAlchemy
            session object.
    """
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        """Context manager protocol start.
        Create a new session and attach repositories to it."""
        self.session = self.session_factory()
        self.users = repo.SqlAlchemyUserRepository(self.session)
        self.collaborators = repo.SqlAlchemyCollaboratorRepository(
            self.session)
        self.clients = repo.SqlAlchemyClientRepository(self.session)
        self.contracts = repo.SqlAlchemyContractRepository(self.session)
        self.events = repo.SqlAlchemyEventRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        """Context manager protocol end.
        Rollback uncommited changes before closing the session."""
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
