import click
from ee_crm.cli_interface.utils import clean_input_fields, normalize_fields, \
    clean_sort, normalize_sort


def cli_prompt(data, no_prompt, prompt_field):
    if no_prompt:
        return data
    for f, help_msg in prompt_field:
        data[f] = (data.get(f) or
                   click.prompt(f'{f.replace('_', ' ')} ({help_msg})'))
    return data


def cli_create(data_input, no_prompt, ctrl_class, prompt_field, keys_map):
    controller = ctrl_class()
    cl_data = clean_input_fields(data_input)
    norm_data = normalize_fields(cl_data, keys_map) or {}
    crea_data = cli_prompt(norm_data, no_prompt, prompt_field)
    controller.create(**crea_data)


def cli_read(pk, filters, sorts, ctrl_class, keys_map):
    controller = ctrl_class()
    cl_filters = clean_input_fields(filters)
    norm_filters = normalize_fields(cl_filters, keys_map)
    cl_sorts = clean_sort(sorts)
    norm_sorts = normalize_sort(cl_sorts, keys_map)
    return controller.read(pk, norm_filters, norm_sorts)


def cli_update(pk, data_input, no_prompt, ctrl_class, prompt_field, keys_map):
    controller = ctrl_class()
    class_dto = controller.read(pk)

    if not click.confirm(f"Update {controller.label} : ({pk}) "
                         f"'{class_dto[0].last_name}' ?"):
        click.echo("Aborted")
        raise SystemExit(1)

    cl_data = clean_input_fields(data_input) or {}
    norm_data = normalize_fields(cl_data, keys_map) or {}
    upd_data = cli_prompt(norm_data, no_prompt, prompt_field)

    controller.update(pk, **upd_data)


def cli_delete(pk, ctrl_class):
    controller = ctrl_class()
    class_dto = controller.read(pk)

    if not click.confirm(f"Delete {controller.label} : ({pk}) "
                         f"'{class_dto[0].last_name}' ?"):
        click.echo("Aborted")
        raise SystemExit(1)

    controller.delete(pk)
