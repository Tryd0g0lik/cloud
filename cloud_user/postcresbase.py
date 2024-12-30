"""
This is a file working only with the PostgreSQL db
"""

import logging

import psycopg2
from psycopg2 import sql

from dotenv_ import (POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD,
                     POSTGRES_PORT, DSN)


def create_database_if_not_exsists(db_name: str) -> bool:
    """
    Def is only checking db. From entry point ('db_name') we receive a db name\
    and her will be look up in inside the postgresql. When returns the 'True' \
    it means what we not have a db name or 'False'.
    :param db_name: str This is a db name.
    :return:bool.
    """
    from logs import configure_logging

    log = logging.getLogger(__name__)
    configure_logging(logging.INFO)
    log.info("[create_database_if_not_exsists] START create the db")

    # CURSOR
    status = False
    connection = object()
    cursor = object()
    try:
        connection = psycopg2.connect(
            user=f"{POSTGRES_USER}",
            password=f"{POSTGRES_PASSWORD}",
            host=f"{POSTGRES_HOST}",
            port=f"{POSTGRES_PORT}",
        )
        # AUTOCOMMIT
        connection.autocommit = True
        cursor = connection.cursor()
        # CHECK availability the tb_name of the postgres
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [db_name]
        )
        exists = cursor.fetchone()
        status_text = "None"
        if not exists:
            sql_text = f"CREATE DATABASE {db_name}"
            cursor.execute(sql.SQL(sql_text))
            status_text = status_text.replace(
                "None",
                f"[{create_database_if_not_exsists.__name__}]: \
База данных '{db_name}' успешно создана.",
            )
            status = True
        else:
            status_text = status_text.replace(
                "None",
                f"[{create_database_if_not_exsists.__name__}]: \
База данных '{db_name}' уже существует.",
            )
    except Exception as e:
        status_text = status_text.replace(
            "None",
            f"[{create_database_if_not_exsists.__name__}] \
Mistake {e.__str__()}",
        )
        raise ValueError(status_text)
    finally:
        # CLOSE the connection
        cursor.close()
        connection.close()
        log.info(status_text)
        return status


# def create_tables(engines):
#     try:
#         # Base.metadata.drop_all(engines)
#         print(f"[create_table]: Drop All")
#
#         Base.metadata.create_all(engines)
#     except Exception as err:
#         print(f"[create_table]: Error => {err.__str__()}")
