from abc import ABC, abstractmethod

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from frogger.config import load_config


class Database(ABC):
    """Abstract class for database controllers."""

    _connection: MySQLConnection = None
    _cursor: MySQLCursor = None

    @abstractmethod
    def _open_connection(self) -> None:
        """Opens connection with database."""
        pass

    @abstractmethod
    def _close_connection(self) -> None:
        """Closes connection with database."""
        pass

    @abstractmethod
    def insert_into_table(self, table: str, fields: str, values: tuple) -> None:
        """Inserts values into table's fields."""
        pass


class EventDatabase(Database):
    """Database controller for events."""

    def __init__(self) -> None:
        database_config = load_config("database")
        self.host: str = database_config["host"]
        self.user: str = database_config["user"]
        self.password: str = database_config["password"]
        self.database: str = database_config["database"]

    def _open_connection(self) -> None:
        self._connection: MySQLConnection = mysql.connector.connect(
            user=self.user, password=self.password,
            host=self.host, database=self.database,
            auth_plugin='mysql_native_password'
        )
        self._cursor: MySQLCursor = self._connection.cursor()

    def _close_connection(self) -> None:
        self._cursor.close()
        self._connection.close()

    def truncate_table(self, table_name: str) -> None:
        """Truncates table in database."""
        self._open_connection()
        self._cursor.execute(f"truncate table {table_name}")
        self._connection.commit()
        self._close_connection()

    def insert_into_table(self, table: str, fields: str, values: tuple[str]) -> None:
        values_string = ", ".join(["%s" for value in values])

        sql = f"INSERT INTO {table} ({fields}) VALUES ({values_string})"

        print(sql)

        self._open_connection()
        self._cursor.execute(sql, values)
        self._connection.commit()
        self._close_connection()

    def insert_list_into_table(self, table: str, fields: str, values_list: list[tuple[str]]) -> None:
        """
        Inserts list of values into database's table.

        List should contain tuples of strings. Example:
        `[ ("value1", "value2"), ("value1", "value2") ]`
        """
        for value_tuple in values_list:
            self.insert_into_table(table, fields, value_tuple)

    def call_proc(self, procname: str) -> None:
        """Calls proc in database."""
        self._open_connection()
        self._cursor.callproc(procname)
        self._connection.commit()
        self._close_connection()
