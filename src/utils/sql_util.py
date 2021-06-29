from typing import Tuple

import mysql.connector.pooling as pooling

import src.utils.log_util as log
from src.data.environment import *

pool = None


class ConnectionPool:
    """ Connection pool to the database """

    def __init__(self):
        self.pool = pooling.MySQLConnectionPool(
            host=DATABASE_URL,
            user=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            pool_name="dodoco",
            db=DATABASE_NAME
        )
        log.info(f"MySQL connection pool is established!")

    def get_connection(self):
        """
        Get a connection from this connection pool
        - None if the connection pool is exhausted

        Returns:
            (pooling.PooledMySQLConnection) connection if pool is not exhausted, otherwise None
        """
        try:
            return self.pool.get_connection()
        except pooling.errors.PoolError as err:
            log.error(f"{err.msg}", flush=True)
            return None


def init_connection_pool():
    global pool
    if pool is not None:
        log.error("A connection pool already exists, ignoring this init request!")
        return
    pool = ConnectionPool()
    log.info("MySQL connection pool initialized successfully!")


class ChainedStatement:
    """ A short-cut for executing multiple SQL statements in order """

    def __init__(self):
        # To ensure connection is closed properly, use "with" statements
        self._enabled = False

    def __enter__(self):
        # Set-up connection
        global pool
        if pool is None:
            init_connection_pool()
            # raise ConnectionError("Connection pool does not exist!")

        self._connection = pool.get_connection()
        if self._connection is None:
            raise ConnectionError("Connection pool refused connection attempt!")

        self.cursor = self._connection.cursor(buffered=True)
        self._enabled = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._enabled = False
        self._close()

    def _close(self):
        """
        Close the current connection
        - when exiting the "with" block, the connection is automatically closed
        """
        self.cursor.close()
        self._connection.close()

    def _check_enabled(self):
        if self._enabled:
            return
        raise ConnectionError("Connection is not enabled! Are you using a \"with\" statement?")

    # Specialized SQL methods
    def insert(self, table, columns, values):
        """
        Insert data into table

        Args:
            table (str): table name
            columns (Tuple[str]): column names in a tuple (if empty, default to all columns)
            values (Tuple[Any]): values to insert, must correspond to "columns"

        Returns:
            (int) affected row count
        """
        sql = f"INSERT INTO {table} "
        if columns:
            sql += "(" + ", ".join(columns) + ") "
        sql += "VALUES (" + ("%s, " * len(values))[:-2] + ");"
        return self.execute(sql, data=values)

    def update(self, table, columns, values, where):
        """
        Update certain parts of the table with new data

        Args:
            table (str): table name
            columns (Tuple[str]): column names in a tuple
            values (Tuple[Any]): values to update, must correspond to "columns"
            where (str): where to update

        Returns:
            (int) affected row count
        """
        sql = f"UPDATE {table} SET "
        sql += ", ".join(f"{column}=%s" for column in columns) + " "
        sql += f"WHERE {where}"
        return self.execute(sql, data=values)

    def delete(self, table, where):
        """
        Delete row(s) from the table

        Args:
            table (str): table name
            where (str): where to delete

        Returns:
            (int) affected row count
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql)

    def delete_all(self, table):
        """
        Delete all records from the table

        Args:
            table (str): table name

        Returns:
            (int) affected row count
        """
        sql = f"DELETE FROM {table}"
        return self.execute(sql)

    # General SQL methods
    def query(self, sql):
        """
        Query the database, check "cursor" attribute for details

        Args:
            sql (str): SQL query statement

        Returns:
            (Iterator) iterator of the result set
        """
        self._check_enabled()
        self._check_empty(sql)
        self.cursor.execute(sql)
        return iter(self.cursor)

    def execute(self, sql, data=None, commit=True):
        """
        Modify the database, check "cursor" attribute for details

        Args:
            sql (str): SQL query statement
            data (Tuple[Any]): query data (corresponds to query statement)
            commit (bool): whether to commit the changes (default True)

        Returns:
            (int) affected row count
        """
        self._check_enabled()
        self._check_empty(sql)
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)
        if commit:
            self._connection.commit()
        return self.cursor.rowcount

    # Utility methods
    @staticmethod
    def _check_empty(sql):
        if not sql:
            log.warning("SQL statement is empty!")


class SQLError(IOError):
    def __init__(self, message):
        super().__init__(message)


if __name__ == "__main__":
    # Code for testing this class
    print("hello (happy) world!")

    pool = ConnectionPool()
    with ChainedStatement() as cs:
        results = []
        row_count = 0
        # results = cs.query(f"SELECT * FROM genshin_mine")
        # results = cs.query(f"DESCRIBE genshin_mine")
        # row_count = cs.insert("receivers", ("display_name", "endpoint", "token"), ("test_receiver", "6_mdIcKwU4ysyfd9N4R4yDsK", "bvp4GejNrxuT6P386d-PZ2TG"))
        # row_count = cs.update("genshin_mine", ("day_stamp",), (178,), "player=\"Geoff\"")
        # row_count = cs.delete_all("api")
        # row_count = cs.execute("DROP TABLE genshin_mine")
        # with open("../data/sql/genshin_mine.sql") as f:
        #     row_count = cs.execute(f.read())
        print(f"Rows affected: {row_count}")
        print(f"Cursor iterator:")
        for i, a in enumerate(results):
            print(f"{i} >> {a}")

    print("done!")
