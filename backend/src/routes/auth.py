from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from src.extensions import db
from src.models.user import User
from src.utils.errors import APIError

bp = Blueprint('auth', __name__, url_prefix='/auth')

class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 2)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email'].lower()).first()
    if existing_user:
        return jsonify({'message': 'Email already registered'}), 409
    
    # Create new user
    user = User(
        name=data['name'].strip(),
        email=data['email'].lower(),
        role='user'
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email'].lower()).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'access': access_token,
        'refresh': refresh_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
    }), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    
    # Verify user still exists
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Create new access token
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access': access_token
    }), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200