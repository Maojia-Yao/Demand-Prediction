import os
from flask import Flask

# Initialize the Flask application
def create_app():
    """Construct the core application"""

    # Create the Flask app object
    app = Flask(__name__)

    # Configure the app from configuration file settings
    app.config.from_object('config.Config')
    
    # Configuring file upload settings
    UPLOAD_FOLDER = 'myapp/static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    return app