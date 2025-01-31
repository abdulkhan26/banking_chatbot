import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLITE_DB = os.getenv('SQLITE_DB', 'database.db')
