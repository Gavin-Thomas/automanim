from flask import Flask, Blueprint
import os

# Import the API blueprint
from .api import api

# Create a Flask application for the backend
app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(api, url_prefix='')

# Create necessary directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils', 'temp')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
