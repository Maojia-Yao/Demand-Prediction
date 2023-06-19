import os
from flask import Flask

# Initialize the Flask application
def create_app():
    """Construct the core application"""

    # Create the Flask app object
    app = Flask(__name__)

    # Configure the app from configuration file settings
    app.config.from_object('config.Config')

    return app