from datetime import datetime

from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork
from ee_crm.services.app.events import EventService

from ee_crm.controllers.app.base import BaseManager, BaseManagerError
from ee_crm.controllers.permission import (
    permission, is_sales, is_support, is_management, event_has_support,
    is_event_associated_support, is_event_associated_salesman
)


class EventManagerError(BaseManagerError):
    pass


class EventManager(BaseManager):
    label = "Event"
    _validate_types_map = {
        "id": int,
        "title": str,
        "start_time": datetime.fromisoformat,
        "end_time": datetime.fromisoformat,
        "location": str,
        "attendee": int,
        "notes": str,
        "supporter_id": int,
        "contract_id": int
    }
    _default_service = EventService(SqlAlchemyUnitOfWork())
    error_cls = EventManagerError

    @permission(requirements=is_sales)
    def create(self, **kwargs):
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

    @permission
    def read(self, pk=None, filters=None, sort=None):
        return super().read(pk=pk, filters=filters, sort=sort)

    @permission(requirements=((~event_has_support &
                               is_event_associated_salesman) |
                              is_event_associated_support))
    def update(self, pk, **kwargs):
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

    @permission(requirements=((~event_has_support &
                               is_event_associated_salesman) |
                              is_event_associated_support))
    def delete(self, pk, **kwargs):
        return super().delete(pk=pk)

    @permission(requirements=is_management)
    def change_support(self, pk, support_id):
        pk = self._validate_pk_type(pk)
        support_id = self._validate_pk_type(support_id)
        self.service.assign_support(pk, support_id)
