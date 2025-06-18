from math import trunc

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.utils import verify_positive_int, verify_bool, \
    verify_positive_float, verify_datetime
from ee_crm.controllers.permission import permission, is_sales, \
    is_management, is_contract_associated_salesman, contract_has_salesman, \
    contract_is_signed
from ee_crm.exceptions import ContractManagerError, InputError
from ee_crm.services.unit_of_work import SqlAlchemyUnitOfWork
from ee_crm.services.app.contracts import ContractService


class ContractManager(BaseManager):
    label = "Contract"
    _validate_types_map = {
        "id": verify_positive_int,
        "total_amount": verify_positive_float,
        "paid_amount": verify_positive_float,
        "signed": verify_bool,
        "client_id": verify_positive_int,
        "created_at": verify_datetime,
    }
    _default_service = ContractService(SqlAlchemyUnitOfWork())
    error_cls = ContractManagerError

    @staticmethod
    def _validate_signed(filters):
        if 'signed' not in filters:
            return filters

        accepted_true = {"yes", "y", "signed", "true"}
        accepted_false = {"n", "no", "not", "not signed", "not-signed",
                          "not_signed", "false"}
        if str(filters['signed']).lower() in accepted_true:
            filters['signed'] = True
        elif str(filters['signed']).lower() in accepted_false:
            filters['signed'] = False
        else:
            filters.pop("signed", None)
        return filters

    @permission(requirements=is_management)
    def create(self, **kwargs):
        create_fields = {
            "total_amount",
            "client_id"
        }
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        return super().create(**create_data)

    @permission
    def read(self, pk=None, filters=None, sort=None):
        if filters:
            filters = self._validate_signed(filters)
        return super().read(pk=pk, filters=filters, sort=sort)

    def update(self, *args, **kwargs):
        raise self.error_cls("Can't update contract directly, "
                                   "use appropriate methods.")

    @permission(requirements=(is_management & ~contract_has_salesman) |
                             (is_sales & is_contract_associated_salesman))
    def delete(self, pk, **kwargs):
        return super().delete(pk=pk)

    @permission(requirements=(is_sales & is_contract_associated_salesman))
    def sign(self, pk):
        pk = self._validate_pk_type(pk)
        self.service.sign_contract(pk)

    @permission(requirements=(is_sales & is_contract_associated_salesman &
                              ~contract_is_signed))
    def change_total(self, pk, total):
        pk = self._validate_pk_type(pk)
        try:
            float(total)
        except ValueError:
            raise self.error_cls(
                f"Total of the contract must be a valid price, "
                f"given : {total}")
        total = trunc(total * 100) / 100
        self.service.modify_total_amount(pk, total)

    @permission(requirements=(is_sales & is_contract_associated_salesman &
                              contract_is_signed))
    def pay(self, pk, amount):
        pk = self._validate_pk_type(pk)
        try:
            float(amount)
        except ValueError:
            raise self.error_cls(
                f"Total of the contract must be a valid price, "
                f"given : {amount}")
        amount = trunc(amount * 100) / 100
        self.service.pay_amount(pk, amount)
