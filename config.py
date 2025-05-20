import os
from dotenv import load_dotenv


load_dotenv()


def get_postgres_uri():
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT')
    dbname = os.getenv('PG_DBNAME')
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
