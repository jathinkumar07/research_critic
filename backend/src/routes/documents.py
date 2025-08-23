import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.extensions import db
from src.models.user import User
from src.models.document import Document
from src.utils.validators import validate_upload_request, generate_safe_filename
from src.utils.security import get_current_user, check_document_ownership
from src.services.pdf_service import extract_text_and_meta

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a PDF document."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    # Validate request
    validation_errors = validate_upload_request(request)
    if validation_errors:
        return jsonify({'message': 'Validation failed', 'errors': validation_errors}), 400
    
    file = request.files['file']
    
    try:
        # Generate safe filename
        safe_filename = generate_safe_filename(file.filename)
        
        # Save file
        upload_dir = current_app.config.get('UPLOAD_DIR', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, safe_filename)
        file.save(file_path)
        
        # Extract text and metadata
        text, word_count, title = extract_text_and_meta(file_path)
        
        # Create document record
        document = Document(
            user_id=current_user.id,
            filename=file.filename,
            stored_path=file_path,
            title=title,
            word_count=word_count
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'document_id': document.id,
            'title': document.title,
            'word_count': document.word_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up file if it was saved
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        return jsonify({'message': f'Upload failed: {str(e)}'}), 500

@bp.route('/<int:document_id>', methods=['GET'])
@jwt_required()
def get_document(document_id):
    """Get document details."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404
    
    # Check ownership (or admin access)
    if not check_document_ownership(document, current_user.id) and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify(document.to_dict()), 200

@bp.route('/', methods=['GET'])
@jwt_required()
def list_documents():
    """List user's documents."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Query documents
    if current_user.role == 'admin':
        # Admin can see all documents
        query = Document.query
    else:
        # Users see only their own documents
        query = Document.query.filter_by(user_id=current_user.id)
    
    documents = query.order_by(Document.uploaded_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'documents': [doc.to_dict() for doc in documents.items],
        'total': documents.total,
        'pages': documents.pages,
        'current_page': page
    }), 200

@bp.route('/<int:document_id>', methods=['DELETE'])
@jwt_required()
def delete_document(document_id):
    """Delete a document."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    document = Document.query.get(document_id)
    if not document:
        return jsonify({'message': 'Document not found'}), 404
    
    # Check ownership (or admin access)
    if not check_document_ownership(document, current_user.id) and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    try:
        # Delete file from filesystem
        if os.path.exists(document.stored_path):
            os.remove(document.stored_path)
        
        # Delete from database (cascade will handle analysis and citations)
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Delete failed: {str(e)}'}), 500