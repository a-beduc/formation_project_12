import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


def get_engine(user, password, host, port, dbname):
    url = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    return create_engine(url, pool_size=50, echo=True)


def get_db_settings_from_env():
    return {'user': os.getenv('PG_USER'),
            'password': os.getenv('PG_PASSWORD'),
            'host': os.getenv('PG_HOST'),
            'port': os.getenv('PG_PORT'),
            'db': os.getenv('PG_DBNAME')}


def get_engine_from_env():
    keys_values = get_db_settings_from_env()
    if None in keys_values.values():
        raise Exception('DB environment variables not set properly')

    return get_engine(keys_values['user'],
                      keys_values['password'],
                      keys_values['host'],
                      keys_values['port'],
                      keys_values['db'])


def create_session():
    engine = get_engine_from_env()
    session = sessionmaker(bind=engine)
    return session()
