from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, ValidationError
from src.extensions import db
from src.models.document import Document
from src.models.analysis import Analysis
from src.models.citation import Citation
from src.utils.security import get_current_user, check_document_ownership, check_analysis_ownership
from src.services.pdf_service import extract_text_and_meta
from src.services.summarizer_service import summarize
from src.services.plagiarism_service import check as check_plagiarism
from src.services.citations_service import validate as validate_citations
from src.services.critique_service import critique

bp = Blueprint('analysis', __name__, url_prefix='/analysis')

class RunAnalysisSchema(Schema):
    document_id = fields.Int(required=True)

@bp.route('/run', methods=['POST'])
@jwt_required()
def run_analysis():
    """Run analysis on a document."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    schema = RunAnalysisSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Get document
    document = Document.query.get(data['document_id'])
    if not document:
        return jsonify({'message': 'Document not found'}), 404
    
    # Check ownership
    if not check_document_ownership(document, current_user.id) and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    # Check if analysis already exists
    if document.analysis:
        return jsonify({'message': 'Analysis already exists for this document'}), 409
    
    try:
        # Extract text from document
        text, word_count, title = extract_text_and_meta(document.stored_path)
        
        if not text or len(text.strip()) < 100:
            return jsonify({'message': 'Document text too short for analysis'}), 400
        
        # Run analysis pipeline
        print(f"Starting analysis for document {document.id}")
        
        # 1. Summarization
        print("Running summarization...")
        summary = summarize(text)
        
        # 2. Plagiarism detection
        print("Running plagiarism check...")
        plagiarism_score = check_plagiarism(text)
        
        # 3. Citation validation
        print("Validating citations...")
        citation_results = validate_citations(text)
        
        # 4. Critique analysis
        print("Running critique analysis...")
        critique_results = critique(text, summary)
        
        # Create analysis record
        analysis = Analysis(
            document_id=document.id,
            summary=summary,
            plagiarism_score=plagiarism_score,
            critique=critique_results
        )
        
        db.session.add(analysis)
        db.session.flush()  # Get analysis ID
        
        # Save citations
        for citation_data in citation_results:
            citation = Citation(
                analysis_id=analysis.id,
                raw_line=citation_data['raw'],
                cleaned_title=citation_data['cleaned_title'],
                status=citation_data['status']
            )
            db.session.add(citation)
        
        db.session.commit()
        
        print(f"Analysis completed for document {document.id}")
        
        # Return results
        return jsonify({
            'analysis_id': analysis.id,
            'summary': analysis.summary,
            'plagiarism_score': analysis.plagiarism_score,
            'critique': analysis.critique,
            'citations': [citation.to_dict() for citation in analysis.citations]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Analysis failed for document {document.id}: {str(e)}")
        return jsonify({'message': f'Analysis failed: {str(e)}'}), 500

@bp.route('/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Get analysis results."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    analysis = Analysis.query.get(analysis_id)
    if not analysis:
        return jsonify({'message': 'Analysis not found'}), 404
    
    # Check ownership
    if not check_analysis_ownership(analysis, current_user.id) and current_user.role != 'admin':
        return jsonify({'message': 'Access denied'}), 403
    
    return jsonify(analysis.to_dict()), 200

@bp.route('/', methods=['GET'])
@jwt_required()
def list_analyses():
    """List user's analyses."""
    current_user = get_current_user()
    if not current_user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # Query analyses
    if current_user.role == 'admin':
        # Admin can see all analyses
        query = Analysis.query
    else:
        # Users see only their own analyses
        query = Analysis.query.join(Document).filter(Document.user_id == current_user.id)
    
    analyses = query.order_by(Analysis.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'analyses': [analysis.to_dict() for analysis in analyses.items],
        'total': analyses.total,
        'pages': analyses.pages,
        'current_page': page
    }), 200

@bp.route('/<int:analysis_id>', methods=['DELETE'])
@jwt_required()
def delete_analysis(analysis_id):
    """Delete an analysis."""
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
        # Delete analysis (cascade will handle citations)
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({'message': 'Analysis deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Delete failed: {str(e)}'}), 500