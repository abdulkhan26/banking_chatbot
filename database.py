import sqlite3
from config import Config

def get_db_connection():
    connection = sqlite3.connect(Config.SQLITE_DB)
    connection.row_factory = sqlite3.Row
    return connection
