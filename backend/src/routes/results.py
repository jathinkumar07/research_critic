from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.extensions import db
from src.models.user import User
from src.models.document import Document
from src.models.analysis import Analysis

results_bp = Blueprint('results', __name__, url_prefix='/api/results')

@results_bp.route('/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_result(analysis_id):
    """
    Retrieve a specific analysis result by ID.
    
    GET /api/results/<id>
    
    Returns:
        200: Analysis result with document details
        403: Access denied (not owner or not admin)
        404: Analysis not found
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get the analysis
    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    # Check if user has access (owner or admin)
    document = analysis.document
    if document.user_id != current_user_id and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Return analysis with document details
    result = analysis.to_dict()
    result['document'] = document.to_dict(include_text=False)  # Don't include full text for performance
    
    return jsonify(result), 200

@results_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_analyses(user_id):
    """
    Retrieve all analyses for a specific user.
    
    GET /api/results/user/<user_id>
    
    Returns:
        200: List of analyses for the user
        403: Access denied (not owner or not admin)
        404: User not found
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user has access (requesting own results or admin)
    if user_id != current_user_id and current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get user's documents with analyses
    documents = Document.query.filter_by(user_id=user_id).all()
    
    results = []
    for document in documents:
        if document.analysis:
            analysis_data = document.analysis.to_dict()
            analysis_data['document'] = document.to_dict(include_text=False)
            results.append(analysis_data)
    
    # Sort by creation date (newest first)
    results.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'analyses': results,
        'total': len(results)
    }), 200

@results_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_analyses():
    """
    Retrieve all analyses for the current user.
    
    GET /api/results/my
    
    Returns:
        200: List of analyses for the current user
    """
    current_user_id = get_jwt_identity()
    return get_user_analyses(current_user_id)

@results_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_analyses():
    """
    Retrieve all analyses (admin only).
    
    GET /api/results/all
    
    Returns:
        200: List of all analyses
        403: Access denied (not admin)
    """
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get all analyses
    analyses = Analysis.query.all()
    
    results = []
    for analysis in analyses:
        analysis_data = analysis.to_dict()
        analysis_data['document'] = analysis.document.to_dict(include_text=False)
        analysis_data['user'] = analysis.document.user.to_dict()
        results.append(analysis_data)
    
    # Sort by creation date (newest first)
    results.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'analyses': results,
        'total': len(results)
    }), 200