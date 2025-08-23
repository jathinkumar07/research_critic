from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def init_extensions(app):
    """Initialize Flask extensions with the app."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Enhanced CORS configuration
    cors_origins = app.config.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    cors.init_app(
        app,
        origins=cors_origins,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
        supports_credentials=True
    )