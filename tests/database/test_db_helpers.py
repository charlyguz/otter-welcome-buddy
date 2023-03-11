import os
import sqlite3
import unittest
from pathlib import Path
from unittest.mock import patch

from otter_welcome_buddy.database.db_helpers import insert_many
from otter_welcome_buddy.database.db_helpers import insert_one
from otter_welcome_buddy.database.dbconn import DbContext


_TEST_DB = "test.db"
_TEST_TABLE_NAME = "test_table"


@patch("otter_welcome_buddy.database.db_helpers.DATA_FILE_PATH", new=_TEST_DB)
class TestDbHelpers(unittest.TestCase):
    def setUp(self):
        self.values = {
            "col_1": 1,
            "col_2": 2,
            "col_3": 3,
            "col_4": 4,
        }

        query = f"""CREATE TABLE IF NOT EXISTS {_TEST_TABLE_NAME}(col_1 integer, col_2 integer, col_3 integer, col_4 integer)"""
        
        with DbContext(Path(_TEST_DB)) as conn:
            if conn.connection is None or conn.cursor is None:
                raise ConnectionError("The connection to the database is not open")
            conn.cursor.execute(query)
            conn.connection.commit()

    def tearDown(self):
        os.remove(_TEST_DB)

    def test_insert_one(self):
        # Arrange
        mocked_columns = list(self.values.keys())
        mocked_values = tuple(self.values.values())

        # Act
        result: int = insert_one(
            table=_TEST_TABLE_NAME,
            columns=mocked_columns,
            values=mocked_values,
        )

        # Assert
        assert result == 1

    def test_insert_many(self):
        # Arrange
        mocked_columns = list(self.values.keys())
        mocked_value = tuple(self.values.values())
        mocked_values = list((mocked_value,) * 3)

        # Act
        result: int = insert_many(
            table=_TEST_TABLE_NAME,
            columns=mocked_columns,
            values=mocked_values,
        )

        # Assert
        assert result == 3
