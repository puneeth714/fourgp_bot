import sqlite3
# create a class to handle the sqlite3 database
class Database_sqlite3:
    def __init__(self, database_name):
        self.database_name = database_name
        