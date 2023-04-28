import sqlite3 as sql


class DB:
    """
    MiGUEL Database
    """
    def __init__(self):
        self.connect = self.create_db()
        self.cursor = self.create_cursor()

    @staticmethod
    def create_db():
        """
        Create SQLite3 database
        :return: sqlite3.Connect
            connect
        """
        connect = sql.connect('data/miguel.db')

        return connect

    def create_cursor(self):
        """
        Create Cursor to edit database
        :return: sqlite3.Connect.Cursor
            cursor
        """
        cursor = self.connect.cursor()

        return cursor




