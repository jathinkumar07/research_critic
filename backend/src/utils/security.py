from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models.user import User

def require_role(required_role):
    """Decorator to require specific role for access."""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            if user.role != required_role and user.role != 'admin':
                return jsonify({'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current user from JWT token."""
    current_user_id = get_jwt_identity()
    if current_user_id:
        return User.query.get(current_user_id)
    return None

def check_document_ownership(document, user_id):
    """Check if user owns the document."""
    return document.user_id == user_id

def check_analysis_ownership(analysis, user_id):
    """Check if user owns the analysis through document ownership."""
    return analysis.document.user_id == user_id