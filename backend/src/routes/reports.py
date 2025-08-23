import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from src.extensions import db
from src.models.analysis import Analysis
from src.utils.security import get_current_user, check_analysis_ownership
from src.services.report_service import generate_report

bp = Blueprint('reports', __name__, url_prefix='/reports')

# In-memory store for generated reports (in production, use database or Redis)
generated_reports = {}

@bp.route('/<int:analysis_id>/generate', methods=['POST'])
@jwt_required()
def generate_analysis_report(analysis_id):
    """Generate PDF report for an analysis."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        return jsonify({'message': 'Analysis not found'}), 404
    
    # Check ownership
    if not check_analysis_ownership(analysis, current_user.id) and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Generate report
        report_id, filepath = generate_report(
            user=current_user,
            document=analysis.document,
            analysis=analysis,
            citations=[citation.to_dict() for citation in analysis.citations]
        )
        
        # Store report info (in production, save to database)
        generated_reports[report_id] = {
            'filepath': filepath,
            'user_id': current_user.id,
            'analysis_id': analysis_id,
            'filename': f"analysis_report_{analysis.document.filename}_{report_id}.pdf"
        }
        
        return jsonify({
            'report_id': report_id
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Report generation failed: {str(e)}'}), 500

@bp.route('/<report_id>/download', methods=['GET'])
@jwt_required()
def download_report(report_id):
    """Download generated report."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    # Check if report exists
    if report_id not in generated_reports:
        return jsonify({'message': 'Report not found'}), 404
    
    report_info = generated_reports[report_id]
    
    # Check ownership (or admin access)
    if report_info['user_id'] != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    # Check if file exists
    filepath = report_info['filepath']
    if not os.path.exists(filepath):
        return jsonify({'message': 'Report file not found'}), 404
    
    try:
        return send_file(
            filepath,
            as_attachment=True,
            download_name=report_info['filename'],
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'message': f'Download failed: {str(e)}'}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def list_reports():
    """List user's generated reports."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    # Filter reports by user (or show all for admin)
    user_reports = []
    for report_id, report_info in generated_reports.items():
        if report_info['user_id'] == current_user.id or current_user.role == 'admin':
            user_reports.append({
                'report_id': report_id,
                'analysis_id': report_info['analysis_id'],
                'filename': report_info['filename']
            })
    
    return jsonify({
        'reports': user_reports
    }), 200

@bp.route('/<report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete a generated report."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    # Check if report exists
    if report_id not in generated_reports:
        return jsonify({'message': 'Report not found'}), 404
    
    report_info = generated_reports[report_id]
    
    # Check ownership (or admin access)
    if report_info['user_id'] != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Delete file from filesystem
        filepath = report_info['filepath']
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Remove from memory store
        del generated_reports[report_id]
        
        return jsonify({'message': 'Report deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Delete failed: {str(e)}'}), 500