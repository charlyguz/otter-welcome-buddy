from collections import namedtuple
from collections.abc import Callable
from pathlib import Path
from sqlite3 import Cursor
from typing import Any

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.database.dbconn import DbContext


def namedtuple_factory(cursor: Cursor, row: tuple) -> tuple:
    """Returns sqlite rows as named tuples"""
    fields: list[str] = [col[0] for col in cursor.description if col[0].isidentifier()]
    named_row = namedtuple("Row", fields)  # type: ignore
    return named_row(*row)


def dict_factory(cursor: Cursor, row: tuple) -> dict:
    """Returns sqlite rows as dict"""
    col_names = [col[0] for col in cursor.description]
    return dict(zip(col_names, row))


def insert_one(table: str, columns: list[str], values: tuple) -> int:
    """Generic insert of one value into a table
    specifying the columns and values desired"""
    row_count = 0
    n_columns = len(columns)
    query = f"""
        INSERT OR REPLACE
        INTO {table}
        ({", ".join(columns)})
        VALUES ({", ".join(["?"] * n_columns)})
    """

    with DbContext(Path(DATA_FILE_PATH)) as conn:
        if conn.connection is None or conn.cursor is None:
            raise ConnectionError("The connection to the database is not open")
        row_count = conn.cursor.execute(query, values).rowcount
        conn.connection.commit()

    return row_count


def insert_many(table: str, columns: list[str], values: list[tuple]) -> int:
    """Generic insert of multiple values into a table
    specifying the columns and values desired"""
    row_count = 0
    n_columns = len(columns)
    query = f"""
        INSERT OR REPLACE
        INTO {table}
        ({", ".join(columns)})
        VALUES ({", ".join(["?"] * n_columns)})
    """

    with DbContext(Path(DATA_FILE_PATH)) as conn:
        if conn.connection is None or conn.cursor is None:
            raise ConnectionError("The connection to the database is not open")
        row_count = conn.cursor.executemany(query, values).rowcount
        conn.connection.commit()

    return row_count


def update(
    table: str,
    columns: list[str],
    values: tuple,
    lookup_key: dict[str, Any] | None = None,
) -> int:
    """Generic update of the specified columns over a table
    limiting with a dictionary of lookup keys"""
    row_count = 0
    query = f"""
        UPDATE {table}
        SET {", ".join(f"{column} = ?" for column in columns)}
    """

    if lookup_key is not None:
        lookup_string = " AND ".join(f"{key} = ?" for key in lookup_key)
        query += f"WHERE {lookup_string}"
        values += tuple(lookup_key.values())

    with DbContext(Path(DATA_FILE_PATH)) as conn:
        if conn.connection is None or conn.cursor is None:
            raise ConnectionError("The connection to the database is not open")
        row_count = conn.cursor.execute(query, values).rowcount
        conn.connection.commit()

    return row_count


def delete(table: str, lookup_key: dict[str, Any] | None = None) -> int:
    """Generic delete over a table limiting
    with a dictionary of lookup keys"""
    row_count = 0
    query = f"""
        DELETE FROM {table}
    """

    values: tuple[Any, ...] = ()
    if lookup_key is not None:
        lookup_string = " AND ".join(f"{key} = ?" for key in lookup_key)
        query += f"WHERE {lookup_string}"
        values = tuple(lookup_key.values())

    with DbContext(Path(DATA_FILE_PATH)) as conn:
        if conn.connection is None or conn.cursor is None:
            raise ConnectionError("The connection to the database is not open")
        row_count = conn.cursor.execute(query, values).rowcount
        conn.connection.commit()

    return row_count


def fetch_one(
    table: str,
    columns: list[str] | None = None,
    lookup_key: dict[str, Any] | None = None,
    row_factory: Callable | None = None,
) -> Any:
    """Generic fetch of one value over a table allowing the selection of the
    specified columns limited with a dictionary of lookup keys"""
    query = f"""
        SELECT {"*" if columns is None else ", ".join(columns)}
        FROM {table}
    """

    values: tuple[Any, ...] = ()
    if lookup_key is not None:
        lookup_string = " AND ".join(f"{key} = ?" for key in lookup_key)
        query += f"WHERE {lookup_string}"
        values = tuple(lookup_key.values())

    with DbContext(Path(DATA_FILE_PATH)) as conn:
        if conn.connection is None or conn.cursor is None:
            raise ConnectionError("The connection to the database is not open")
        if row_factory is not None:
            conn.cursor.row_factory = row_factory
        res = conn.cursor.execute(query, values).fetchone()

    return res


def fetch_all(
    table: str,
    columns: list[str] | None = None,
    lookup_key: dict[str, Any] | None = None,
    row_factory: Callable | None = None,
) -> list:
    """Generic fetch of multiple values over a table allowing the selection of the
    specified columns limited with a dictionary of lookup keys"""
    query = f"""
        SELECT {"*" if columns is None else ", ".join(columns)}
        FROM {table}
    """

    values: tuple[Any, ...] = ()
    if lookup_key is not None:
        lookup_string = " AND ".join(f"{key} = ?" for key in lookup_key)
        query += f"WHERE {lookup_string}"
        values = tuple(lookup_key.values())

    with DbContext(Path(DATA_FILE_PATH)) as conn:
        if conn.connection is None or conn.cursor is None:
            raise ConnectionError("The connection to the database is not open")
        if row_factory is not None:
            conn.cursor.row_factory = row_factory
        res = conn.cursor.execute(query, values).fetchall()

    return res
