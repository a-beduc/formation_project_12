from ee_crm.adapters.orm import start_mappers
from ee_crm.cli_interface.entry_point import cli


def main():
    start_mappers()
    try:
        cli()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
