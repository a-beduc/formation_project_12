"""Generic function to process flow of action that are used mainly for
CRUD operation. Specific are injected through signatures of functions.

Functions:
    cli_clean   # Helper that format filters and sorts
    cli_prompt  # Helper that prompt user for missing information
    cli_confirm # Prompt confirmation and throw expected error if not
    cli_create  #
    cli_read    #
    cli_update  #
    cli_delete  #
    cli_mine    #
"""
import click

from ee_crm.cli_interface.utils import clean_input_fields, normalize_fields, \
    clean_sort, normalize_sort


def cli_clean(filters, sorts, keys_map):
    """Helper to transform input from click into a format usable by
    the controller layer.

    Args:
        filters (iter(tuple[str, str])): Each tuples contains a pairs of
            value that will be used as key-value pairs for a dict.
        sorts (tuple[str]): Ordered keyword to use for sorting.
            Processed to extract direction of sorting (asc vs desc)
        keys_map (dict): Injection of accepted keyword to map value
            to a keyword usable by the controller layer.

    Returns:
        Tuple(dict, tuple(tuple[str, bool])): packs of datas usable by
            the controller layer.
    """
    cl_filters = clean_input_fields(filters)
    norm_filters = normalize_fields(cl_filters, keys_map)
    cl_sorts = clean_sort(sorts)
    norm_sorts = normalize_sort(cl_sorts, keys_map)
    return norm_filters, norm_sorts


def cli_prompt(data, no_prompt, prompt_field):
    """Helper that will ask the user for input for fields that don't
    have information linked to them. If data was previously provided,
    it uses it instead of prompting.

    Args:
        data (dict): Dictionary of data.
        no_prompt (bool): Whether the user wants to be prompted for
            missing fields.
        prompt_field (tuple(tuple[str, str])): Index 0 of tuple is the
            field name and index 1 of tuple is the message printed to
            help the user.

    Returns:
        dict: Complete dictionary of data.
    """
    if no_prompt:
        return data
    for f, help_msg in prompt_field:
        data[f] = (data.get(f) or
                   click.prompt(f'{f.replace('_', ' ')} ({help_msg})'))
    return data


def cli_confirm(pk, ctrl_inst, msg, action="update"):
    """Helper to ask the user to confirm the action before proceeding
    with a destructive action. Signature is mainly used for loggings,
    when an exception occurs.

    Args:
        pk (int): The primary key of the resource.
        ctrl_inst (Controller): Controller instance.
        msg (str): Message to display to the user.
        action (str): The action to take.

    Raises:
        BaseManagerError: An error specific to the Manager used.
    """
    if not click.confirm(
            f"{action.capitalize()} {ctrl_inst.label} : ({pk}) ?"):
        err = ctrl_inst.error_cls("Aborted by user")
        err.threat = "warning"
        err.tips = msg
        raise err


def cli_create(data_input, no_prompt, ctrl_class, prompt_field, keys_map):
    """Format data received and gives it to the controller layer to
    start the resource creation service.

    Args:
        data_input (iter(tuple[str, str])): the tuples contain
            information about the new resource.
        no_prompt (bool): Whether the user wants to be prompted for
            missing fields of information.
        ctrl_class (BaseManager): Controller class, specific for each
            resource.
        prompt_field (tuple(tuple[str, str])): Index 0 of tuple is the
            field name and index 1 of tuple is the message printed to
            help the user.
        keys_map (dict): Injection of accepted keyword to map value
            to a keyword usable by the controller layer.

    Returns:
        BaseManager.create: Output of controller layer create method.
    """
    controller = ctrl_class()
    cl_data = clean_input_fields(data_input)
    norm_data = normalize_fields(cl_data, keys_map) or {}
    crea_data = cli_prompt(norm_data, no_prompt, prompt_field)
    return controller.create(**crea_data)


def cli_read(pk, filters, sorts, ctrl_class, keys_map):
    """Format data received and gives it to the controller layer to
    do a query.

    Args:
        pk (int): The primary key of the resource.
        filters (iter(tuple[str, str])): Each tuples contains a pairs of
            value that will be used as key-value pairs for a dict.
        sorts (tuple[str]): Ordered keyword to use for sorting.
            Processed to extract direction of sorting (asc vs desc)
        ctrl_class (BaseManager): Controller class, specific for each
            resource.
        keys_map (dict): Injection of accepted keyword to map value
            to a keyword usable by the controller layer.

    Returns:
        BaseManager.read: Output of controller layer read method.
    """
    controller = ctrl_class()
    norm_filters, norm_sorts = cli_clean(filters, sorts, keys_map)
    return controller.read(pk, norm_filters, norm_sorts)


def cli_update(pk, data_input, no_prompt, ctrl_class, prompt_field, keys_map):
    """Format data received and gives it to the controller layer to
    update a specific resource.

    Args:
        pk (int): The primary key of the resource.
        data_input (iter(tuple[str, str])): the tuples contain
            information about the new resource.
        no_prompt (bool): Whether the user wants to be prompted for
            missing fields of information.
        ctrl_class (BaseManager): Controller class, specific for each
            resource.
        prompt_field (tuple(tuple[str, str])): Index 0 of tuple is the
            field name and index 1 of tuple is the message printed to
            help the user.
        keys_map (dict): Injection of accepted keyword to map value
            to a keyword usable by the controller layer.
    """
    controller = ctrl_class()

    cli_confirm(pk, controller,
                msg='You must press "Y" to confirm update, try again')

    cl_data = clean_input_fields(data_input) or {}
    norm_data = normalize_fields(cl_data, keys_map) or {}

    if not no_prompt:
        if not click.confirm(
                "Do you want be asked input about every fields ?"):
            no_prompt = True

    upd_data = cli_prompt(norm_data, no_prompt, prompt_field)

    controller.update(pk, **upd_data)


def cli_delete(pk, ctrl_class):
    """Select a specific resource to delete.

    Args:
        pk (int): The primary key of the resource.
        ctrl_class (BaseManager): Controller class, specific for each
            resource.
    """
    controller = ctrl_class()

    cli_confirm(pk, controller,
                msg='You must press "Y" to confirm deletion, try again',
                action="delete")

    controller.delete(pk)


def cli_mine(filters, sorts, ctrl_class, keys_map):
    """Format data received and gives it to the controller layer to do
    a specific query on the database where the user is linked (loosely)
    to the target resource.

    Args:
        filters (iter(tuple[str, str])): Each tuples contains a pairs of
            value that will be used as key-value pairs for a dict.
        sorts (tuple[str]): Ordered keyword to use for sorting.
            Processed to extract direction of sorting (asc vs desc)
        ctrl_class (BaseManager): Controller class, specific for each
            resource.
        keys_map (dict): Injection of accepted keyword to map value
            to a keyword usable by the controller layer.

    Returns:
        BaseManager.user_associated_resource: Output of the specific
            BaseManager.user_associated_resource method.
    """
    controller = ctrl_class()
    norm_filters, norm_sorts = cli_clean(filters, sorts, keys_map)
    return controller.user_associated_resource(norm_filters, norm_sorts)
