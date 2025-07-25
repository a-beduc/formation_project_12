"""Controller class for the Contract resource operations.

The update methods should never be called and have been overridden as a
safety measure.

Classes
    ContractManager # It expands BaseManager to add contract specific
                    # operations.
"""
from math import trunc
from typing import override

from ee_crm.controllers.app.base import BaseManager
from ee_crm.controllers.auth.permission import permission
from ee_crm.controllers.auth.predicate import \
    is_contract_associated_salesman, is_management, contract_is_signed, \
    contract_has_salesman
from ee_crm.controllers.default_uow import DEFAULT_UOW
from ee_crm.controllers.utils import verify_positive_int, verify_bool, \
    verify_positive_float, verify_datetime
from ee_crm.exceptions import ContractManagerError
from ee_crm.loggers import log_sentry_message_event, setup_file_logger
from ee_crm.services.app.contracts import ContractService


class ContractManager(BaseManager):
    """Controller for Contract resource.

    Inherits from BaseManager, only public attributes differences are
    documented below.

    Attributes
        label: "Contract"
        error_cls: ContractManagerError
        service (ee_crm.services.app.contracts.ContractService): The service
            class to start operations with.
    """
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
        """Local logging setup for logging contract resource actions.

        Args
            action (str): The performed action. (ex: Update).
            result (str): The result of the action.
                (ex: Updated Contract).
            resource_id (int): The id of the resource who was modified.
                (ex: 6).
            accountable_id (int): The id of the contract who
                modified the resource. (ex: 6).
        """
        logger = setup_file_logger(name=__name__, filename="ACID")
        logger.info(f'controller ::: Contract ::: {action} ::: '
                    f'By collaborator ({accountable_id}) ::: '
                    f'{result} ({resource_id})')

    def _sentry_logging_db_action(self, action, resource_id, accountable_id,
                                  message, level="info", **kwargs):
        """Sentry logging setup for logging contract resource actions.

        Args
            action (str): The performed action. (ex: Sign).
            resource_id (int): The id of the resource who was modified.
                (ex: 6).
            accountable_id (int): The id of the collaborator who
                modified the resource. (ex: 6).
            message (str): The message to log.
                (ex: Contract signed).
            level (str): The level of the log message.
            kwargs (dict): extra arguments passed to the logger.
        """
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
        """Helper that transform input for the signed key in a bool if
        possible.

        Args
            filters (dict): keyword arguments and context.

        Returns
            dict: The input dict with a modified value for the key
                'signed' if it existed.
        """
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

    @override
    @permission("contract:create")
    def create(self, **kwargs):
        """See BaseManager.create

        Differences
            * limit accepted keyword parameters passed to the service.
        """
        create_fields = {
            "total_amount",
            "client_id"
        }
        create_data = {k: v for k, v in kwargs.items() if k in create_fields}
        return super().create(**create_data)

    @override
    @permission("contract:read")
    def read(self, pk=None, filters=None, sort=None):
        """See BaseManager.read

        Differences
            * Transform input for the signed key in a bool.
        """
        if filters:
            filters = self._validate_signed(filters)
        return super().read(pk=pk, filters=filters, sort=sort)

    @override
    def update(self, *args, **kwargs):
        """Raise an error if used, contract should be modified through
        specific methods.

        Raises
            ContractManagerError: If used."""
        err = self.error_cls("Can't update contract directly, "
                             "use appropriate methods.")
        err.tips = ("You can't update a contract directly, please use "
                    "appropriate commands.")
        raise err

    @override
    @permission("contract:delete_own", "contract:delete_unassigned",
                abac=(is_contract_associated_salesman |
                      (is_management & ~contract_has_salesman)))
    def delete(self, pk, **kwargs):
        """See BaseManager.delete"""
        return super().delete(pk=pk)

    @permission("contract:sign_own",
                abac=is_contract_associated_salesman)
    def sign(self, pk, **kwargs):
        """Method to sign a contract, logged.

        Args
            pk (int): The primary key of the contract.
            kwargs (dict): extra arguments passed to the logger.
        """
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
        """Method to change the total amount to pay for a contract.

        Args
            pk (int): The primary key of the contract.
            total (int|float): The new total amount to pay for the
                contract.
        """
        pk = self._validate_pk_type(pk)
        total = self._validate_types("total_amount", total)
        total = trunc(total * 100) / 100
        self.service.modify_total_amount(pk, total)

    @permission("contract:pay_own",
                abac=(is_contract_associated_salesman & contract_is_signed))
    def pay(self, pk, amount):
        """Method to pay a certain amount of a contract.

        Args
            pk (int): The primary key of the contract.
            amount (float|int): The amount pay.
        """
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
        """Method to retrieve the user's associated contracts.

        Args
            only_unpaid (bool): If True, only the unpaid contract.
            only_unsigned (bool): If True, only the unsigned contract.
            only_no_event (bool): If True, only the contract w/o events.
            filters (dict): The keywords filters parameters to apply to
                the query.
            sort (iter(tuple[str, str])): The sort to apply to the
                query.
            kwargs (dict): extra arguments, like JWT payload.

        Returns
            Tuple[ContractDTO]: A tuple containing the result of the
                query.
        """
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
        """Method to retrieve the contracts without associated clients.

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
        validated_filters['client_id'] = None
        output_dto = self.service.filter(sort=sort, **validated_filters)
        return output_dto
