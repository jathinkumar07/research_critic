from flask import jsonify, current_app
import logging
import os
from datetime import datetime

class APIError(Exception):
    """Custom API exception."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['code'] = self.status_code
        return rv

def setup_logging(app):
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    log_level = logging.DEBUG if app.debug else logging.INFO
    log_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    
    # File handler for all logs
    log_file = os.path.join(logs_dir, 'app.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Error file handler for errors only
    error_file = os.path.join(logs_dir, 'error.log')
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    if app.debug:
        root_logger.addHandler(console_handler)
    
    # Configure Flask app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(log_level)

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    # Setup logging first
    setup_logging(app)
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        app.logger.error(f"API Error: {error.message} (Status: {error.status_code})")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"Bad request: {error}")
        return jsonify({'message': 'Bad request', 'code': 400}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        app.logger.warning(f"Unauthorized access: {error}")
        return jsonify({'message': 'Authentication required', 'code': 401}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        app.logger.warning(f"Forbidden access: {error}")
        return jsonify({'message': 'Access forbidden', 'code': 403}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.info(f"Resource not found: {error}")
        return jsonify({'message': 'Resource not found', 'code': 404}), 404
    
    @app.errorhandler(413)
    def file_too_large(error):
        app.logger.warning(f"File too large: {error}")
        return jsonify({'message': 'File too large', 'code': 413}), 413
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        app.logger.warning(f"Unprocessable entity: {error}")
        return jsonify({'message': 'Unprocessable entity', 'code': 422}), 422
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        app.logger.warning(f"Rate limit exceeded: {error}")
        return jsonify({'message': 'Rate limit exceeded', 'code': 429}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({'message': 'Internal server error', 'code': 500}), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f"Unexpected error: {error}", exc_info=True)
        return jsonify({
            'message': 'An unexpected error occurred',
            'code': 500
        }), 500