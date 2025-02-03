import os

class Config:
    """Base configuration class with default settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Absolute path to current directory
    SQLITE_DB = os.getenv('SQLITE_DB', os.path.join(BASE_DIR, 'database.db'))
    DEBUG = False

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
