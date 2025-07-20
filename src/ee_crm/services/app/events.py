"""Service layer responsible for Event domain entities.

Classes
    EventService    # Business operations for events.
"""
from ee_crm.domain.model import Event, Role
from ee_crm.exceptions import EventServiceError
from ee_crm.services.app.base import BaseService
from ee_crm.services.dto import EventDTO


class EventService(BaseService):
    """Manage events business operations.

    Attributes
        uow (AbstractUnitOfWork): Unit of work exposing repositories.
    """
    def __init__(self, uow):
        super().__init__(
            uow,
            Event,
            EventDTO,
            EventServiceError,
            "events"
        )

    def create(self, contract_id=None, **kwargs):
        """Create an event for an existing signed contract.

        Args
            contract_id (int): Primary key of the contract.
            **kwargs (Any): Keyword arguments used to filter entities.

        Returns
            tuple[EventDTO]: Tuple containing the dto of the newly
                created event.

        Raises
            EventServiceError: If no contract is found, the found
                contract is not signed, or the found contract already
                has a linked event.
        """
        with self.uow:
            contract = self.uow.contracts.get(contract_id)
            if contract is None:
                err = EventServiceError(f"No contract found.")
                err.tips = (f"The contract_id {contract_id} isn't linked to a "
                            f"contract in the database.")
                raise err
            if not contract.signed:
                err = EventServiceError("Can't create event for unsigned "
                                        "contracts")
                err.tips = ("The contract linked to the event hasn't been "
                            "signed yet. It must be signed before an event "
                            "can be created.")
                raise err
            if getattr(contract, "event", None) is not None:
                err = EventServiceError("Event already exists.")
                err.tips = (f"The event for this contract already exists. See "
                            f"event ({contract.event.id}).")
                raise err
        obj_value = {k: v for k, v in kwargs.items()
                     if k in self.model_cls.updatable_fields()}
        return super().create(contract_id=contract_id, **obj_value)

    def assign_support(self, event_id, supporter_id=None):
        """Assign a collaborator as the support of the event.

        Args
            event_id (int): Primary key of the event.
            supporter_id (int): Primary key of the collaborator.

        Raises
            EventServiceError: If no collaborator found, the found
                collaborator does not have the SUPPORT role.
        """
        with self.uow:
            if supporter_id is not None:
                supporter = self.uow.collaborators.get(supporter_id)
                if supporter is None:
                    err = self.error_cls("Can't find collaborator")
                    err.tips = (f"The supporter_id {supporter_id} isn't "
                                f"linked to a collaborator in the database.")
                    raise err
                if supporter.role != Role.SUPPORT:
                    err = self.error_cls("Can only assign supports to event")
                    err.tips = (f"The supporter_id {supporter_id} isn't linked "
                                f"to a collaborator with the role SUPPORTER "
                                f"in the database.")
                    raise err

            event = self._repo.get(event_id)
            event.supporter_id = supporter_id
            self.uow.commit()
