from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ee_crm.adapters import repositories as repo
from ee_crm.config import get_postgres_uri


class AbstractUnitOfWork(ABC):
    users: repo.AbstractRepository
    collaborators: repo.AbstractRepository
    clients: repo.AbstractRepository
    contracts: repo.AbstractRepository
    events: repo.AbstractRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abstractmethod
    def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def _commit(self):
        raise NotImplementedError


# launched at import time, may be better to add a factory func that yield Sess
DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(get_postgres_uri()),
    autoflush=True,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.users = repo.SqlAlchemyUserRepository(self.session)
        self.collaborators = repo.SqlAlchemyCollaboratorRepository(
            self.session)
        self.clients = repo.SqlAlchemyClientRepository(self.session)
        self.contracts = repo.SqlAlchemyContractRepository(self.session)
        self.events = repo.SqlAlchemyEventRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
