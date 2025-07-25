"""Controller class for the Event resource operations.

Classes
    EventManager    # It expands BaseManager to add event specific
                    # operations.
"""
from typing import override

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.auth.predicate import event_has_support, \
    is_event_associated_salesman, is_event_associated_support, is_management
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_string, \
    verify_datetime
from ee_crm.exceptions import EventManagerError
from ee_crm.services.app.events import EventService


class EventManager(BaseManager):
    """Controller for Event resource.

    Inherits from BaseManager, only public attributes differences are
    documented below.

    Attributes
        label: "Event"
        error_cls: EventManagerError
        service (ee_crm.services.app.events.EventService): The service
            class to start operations with.
    """
    label = "Event"
    _validate_types_map = {
        "id": verify_positive_int,
        "title": verify_string,
        "start_time": verify_datetime,
        "end_time": verify_datetime,
        "location": verify_string,
        "attendee": verify_positive_int,
        "notes": verify_string,
        "supporter_id": verify_positive_int,
        "contract_id": verify_positive_int
    }
    _default_service = EventService(DEFAULT_UOW())
    error_cls = EventManagerError

    @override
    @permission("event:create")
    def create(self, **kwargs):
        """See BaseManager.create

        Differences
            * limit accepted keyword parameters passed to the service.
        """
        create_fields = {
            "title",
            "start_time",
            "end_time",
            "location",
            "attendee",
            "notes",
            "contract_id"
        }
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        return super().create(**create_data)

    @override
    @permission("event:read")
    def read(self, pk=None, filters=None, sort=None):
        """See BaseManager.read"""
        return super().read(pk=pk, filters=filters, sort=sort)

    @override
    @permission("event:update_own", "event:update_unassigned",
                abac=((~event_has_support & is_event_associated_salesman) |
                      is_event_associated_support))
    def update(self, pk, **kwargs):
        """See BaseManager.update

        Differences
            * limit accepted keyword parameters passed to the service.
        """
        update_fields = {
            "title",
            "start_time",
            "end_time",
            "location",
            "attendee",
            "notes"
        }
        update_data = {k: v for k, v in kwargs.items() if k in update_fields}
        return super().update(pk=pk, **update_data)

    @override
    @permission("event:delete_unassigned", "event:delete",
                abac=((~event_has_support & is_event_associated_salesman) |
                      is_management))
    def delete(self, pk, **kwargs):
        """See BaseManager.delete"""
        return super().delete(pk=pk)

    @permission("event:modify_support")
    def change_support(self, pk, support_id=None, unassign_flag=False):
        """Method that pilot the modification of the support of an
        event.

        Args
            pk (int): The primary key/ID of the collaborator.
            support_id (int|None): The id of the support.
            unassign_flag (bool|None): If raised, remove support.
        """
        pk = self._validate_pk_type(pk)
        if unassign_flag:
            support_id = None
        else:
            support_id = self._validate_pk_type(support_id)
        self.service.assign_support(pk, support_id)

    @permission("event:read")
    def user_associated_resource(self, filters, sort, **kwargs):
        """Method that pilot the operation to retrieve the events
        for which the support is the user.

        Args
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.
            **kwargs (dict): Keyword arguments to pass the context.

        Returns
            tuple[dataclass]: A tuple containing the result of the
                query.
        """
        if filters is None:
            filters = {}
        filters['supporter_id'] = kwargs['auth']['c_id']
        return super().read(pk=None, filters=filters, sort=sort)

    @permission("event:read")
    def unassigned_events(self, filters, sort):
        """Method that pilot the operation to retrieve the events
        that have no support assigned.

        Args
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.

        Returns
            Tuple[EventDTO]: A tuple containing the result of the
                query.
        """
        if filters is None:
            filters = {}
        validated_filters = self._validate_fields(filters)
        validated_filters['supporter_id'] = None
        output_dto = self.service.filter(sort=sort, **validated_filters)
        return output_dto

    @permission("event:read")
    def orphan_events(self, filters, sort):
        """Method to retrieve the events without associated contracts.

        Args
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.

        Returns
            Tuple[ContractDTO]: A tuple containing the result of the
                query.
        """
        if filters is None:
            filters = {}
        validated_filters = self._validate_fields(filters)
        validated_filters['contract_id'] = None
        output_dto = self.service.filter(sort=sort, **validated_filters)
        return output_dto
