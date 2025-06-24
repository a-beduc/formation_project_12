from math import trunc

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.predicate import \
    is_contract_associated_salesman, is_management, contract_is_signed, \
    contract_has_salesman
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_bool, \
    verify_positive_float, verify_datetime
from ee_crm.controllers.auth.permission import permission
from ee_crm.exceptions import ContractManagerError
from ee_crm.loggers import log_sentry_message_event, setup_file_logger
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
    _default_service = ContractService(DEFAULT_UOW())
    error_cls = ContractManagerError

    @staticmethod
    def _local_logging_db_action(action, result, resource_id, accountable_id):
        logger = setup_file_logger(name=__name__, filename="ACID")
        logger.info(f'controller ::: Contract ::: {action} ::: '
                    f'By collaborator ({accountable_id}) ::: '
                    f'{result} ({resource_id})')

    def _sentry_logging_db_action(self, action, resource_id, accountable_id,
                                  message, level="info", **kwargs):
        tags = {
            "action": action,
            "resource": self.label.lower(),
            "resource_id": str(resource_id),
            "accountable_id": str(accountable_id)}
        extra = kwargs.get('extra', None)
        user = {"id": accountable_id}
        log_sentry_message_event(message, level,
                                 tags=tags, extra=extra, user=user)

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

    @permission("contract:create")
    def create(self, **kwargs):
        create_fields = {
            "total_amount",
            "client_id"
        }
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        return super().create(**create_data)

    @permission("contract:read")
    def read(self, pk=None, filters=None, sort=None):
        if filters:
            filters = self._validate_signed(filters)
        return super().read(pk=pk, filters=filters, sort=sort)

    def update(self, *args, **kwargs):
        err = self.error_cls("Can't update contract directly, "
                             "use appropriate methods.")
        err.tips = ("You can't update a contract manually, please use "
                    "appropriate commands.")
        raise err

    @permission("contract:delete_own", "contract:delete_unassigned",
                abac=(is_contract_associated_salesman |
                      (is_management & ~contract_has_salesman)))
    def delete(self, pk, **kwargs):
        return super().delete(pk=pk)

    @permission("contract:sign_own",
                abac=is_contract_associated_salesman)
    def sign(self, pk, **kwargs):
        pk = self._validate_pk_type(pk)
        self.service.sign_contract(pk)

        resource_id = pk
        accountable_id = kwargs.get('auth')['c_id']
        self._local_logging_db_action("Sign",
                                      "Contract signed",
                                      resource_id,
                                      accountable_id)

        self._sentry_logging_db_action("Sign",
                                       resource_id,
                                       accountable_id,
                                       "Contract signed",
                                       extra={"contract_id": pk})

    @permission("contract:modify_total_own",
                abac=(is_contract_associated_salesman & ~contract_is_signed))
    def change_total(self, pk, total):
        pk = self._validate_pk_type(pk)
        total = self._validate_types("total_amount", total)
        total = trunc(total * 100) / 100
        self.service.modify_total_amount(pk, total)

    @permission("contract:pay_own",
                abac=(is_contract_associated_salesman & contract_is_signed))
    def pay(self, pk, amount):
        pk = self._validate_pk_type(pk)
        amount = self._validate_types("paid_amount", amount)
        amount = trunc(amount * 100) / 100
        self.service.pay_amount(pk, amount)

    @permission("contract:read")
    def user_associated_contracts(self,
                                  only_unpaid,
                                  only_unsigned,
                                  only_no_event,
                                  filters,
                                  sort, **kwargs):
        collaborator_id = int(kwargs['auth']['c_id'])
        if filters is None:
            validated_filters = {}
        else:
            filters = self._validate_signed(filters)
            validated_filters = self._validate_fields(filters)
        return self.service.retrieve_collaborator_contracts(
            collaborator_id,
            only_unpaid,
            only_unsigned,
            only_no_event,
            sort, **validated_filters)

    @permission("contract:read")
    def orphan_contracts(self, filters, sort):
        if filters is None:
            filters = {}
        validated_filters = self._validate_fields(filters)
        validated_filters['client_id'] = None
        output_dto = self.service.filter(sort=sort, **validated_filters)
        return output_dto
