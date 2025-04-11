from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import argparse
import socket
import logging
from backend.api import api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

# Create necessary directories
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'temp')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MEDIA_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/media/<path:filename>')
def serve_media(filename):
    """Serve media files"""
    return send_from_directory(MEDIA_FOLDER, filename)

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    port = start_port
    attempts = 0
    
    while attempts < max_attempts:
        if not is_port_in_use(port):
            return port
        port += 1
        attempts += 1
    
    # If we couldn't find an available port, return a default
    return 8080

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Manim Animation Generator app')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--production', action='store_true', help='Run in production mode with gunicorn')
    
    args = parser.parse_args()
    
    if args.production:
        # In production mode, we'll use gunicorn which will handle port binding
        logger.info("Running in production mode - Gunicorn will handle server startup")
        # This block won't execute as gunicorn will import this file
        pass
    else:
        # Check if the specified port is available, if not find an available one
        port = args.port
        if is_port_in_use(port):
            logger.warning(f"Port {port} is already in use")
            port = find_available_port(port)
            logger.info(f"Using port {port} instead")
        
        # Run the application in development mode
        logger.info(f"Starting development server on {args.host}:{port}")
        app.run(host=args.host, port=port, debug=args.debug)
