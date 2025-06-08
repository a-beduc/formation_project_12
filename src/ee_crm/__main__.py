from ee_crm.adapters.orm import start_mappers
from ee_crm.cli_interface.entry_point import cli


if __name__ == '__main__':
    start_mappers()
    cli()
