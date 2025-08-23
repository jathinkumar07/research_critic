import os
from flask import Flask
from flask_cors import CORS

def create_test_app():
    """Flask application factory for testing."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
    
    # Initialize CORS
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Register only the simple analyze blueprint
    from src.routes.simple_analyze import simple_analyze_bp
    app.register_blueprint(simple_analyze_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Test API is running'}, 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return {'message': 'Test API', 'version': '1.0.0'}, 200
    
    return app

if __name__ == '__main__':
    app = create_test_app()
    app.run(debug=True, host='0.0.0.0', port=5000)