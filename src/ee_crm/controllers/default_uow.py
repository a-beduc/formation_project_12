"""Settings for the unit_of_work used by controller layer.

Constants
    DEFAULT_UOW # Unit of work implementation
"""
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork


DEFAULT_UOW = SqlAlchemyUnitOfWork
