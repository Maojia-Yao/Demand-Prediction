"""Flask configuration variables"""
from os import environ

class Config:
    """Set Flask configuration from environment variables"""

    # Flask configuration
    FLASK_APP = environ.get("FLASK_APP")
    FLASK_ENV = environ.get("FLASK_ENV")

    SECRET_KEY = environ.get("SECRET_KEY")
