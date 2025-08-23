from flask import Blueprint, request, jsonify
from src.services.factcheck_service import extract_claims, fact_check_claims
from src.services.pdf_service import extract_text_and_meta
from src.models.document import Document

factcheck_bp = Blueprint("factcheck", __name__)


@factcheck_bp.route("/run", methods=["POST"])
def run_factcheck():
    """
    Run fact-check analysis on document text or provided text.
    
    POST /api/factcheck/run
    
    Request body (JSON):
        - Option 1: {"document_id": 123} - fact-check text from database document
        - Option 2: {"text": "..."} - fact-check provided text directly
    
    Returns:
        200: {
            "claims": [
                {
                    "claim": "original sentence",
                    "status": "verified|contradicted|no_verdict|api_error|not_configured",
                    "fact_checks": [...],
                    "error": null or "error message"
                }
            ],
            "source": "google_factcheck"
        }
        400: {"error": "error message"} - for validation errors
        404: {"error": "document not found"} - if document_id doesn't exist
        500: {"error": "error message"} - for server errors
    """
    try:
        # Parse JSON payload
        payload = request.get_json(force=True, silent=True) or {}
        text = None
        
        # Handle document_id input
        if "document_id" in payload:
            doc_id = payload.get("document_id")
            
            if not isinstance(doc_id, int):
                return jsonify({
                    "status": "error",
                    "message": "document_id must be an integer",
                    "data": None
                }), 400
            
            # Find document in database
            document = Document.query.get(doc_id)
            if not document:
                return jsonify({
                    "status": "error",
                    "message": "document not found",
                    "data": None
                }), 404
            
            try:
                # Extract text from stored PDF file
                text, word_count, title = extract_text_and_meta(document.stored_path)
                
                if not text or len(text.strip()) < 50:
                    return jsonify({
                        "status": "error",
                        "message": "Document text too short for fact-checking",
                        "data": None
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Failed to extract text from document: {str(e)}",
                    "data": None
                }), 500
        
        # Handle direct text input
        elif "text" in payload:
            text = payload.get("text")
            
            if not isinstance(text, str):
                return jsonify({
                    "status": "error",
                    "message": "text must be a string",
                    "data": None
                }), 400
                
            if not text or len(text.strip()) < 50:
                return jsonify({
                    "status": "error",
                    "message": "Text too short for fact-checking",
                    "data": None
                }), 400
        
        # No valid input provided
        else:
            return jsonify({
                "status": "error",
                "message": "Provide either 'document_id' (integer) or 'text' (string) in JSON body",
                "data": None
            }), 400

        # Extract claims from text
        try:
            claims = extract_claims(text)
            
            if not claims:
                return jsonify({
                    "status": "success",
                    "message": "No factual claims found in the text",
                    "data": {
                        "claims": [],
                        "source": "google_factcheck",
                        "total_claims": 0
                    }
                }), 200
                
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to extract claims: {str(e)}",
                "data": None
            }), 500

        # Fact-check the extracted claims
        try:
            fact_check_results = fact_check_claims(claims)
            
            return jsonify({
                "status": "success",
                "message": f"Fact-checked {len(fact_check_results)} claims successfully",
                "data": {
                    "claims": fact_check_results,
                    "source": "google_factcheck",
                    "total_claims": len(fact_check_results)
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Fact-checking failed: {str(e)}",
                "data": None
            }), 500
            
    except Exception as e:
        # Catch-all for unexpected errors
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}",
            "data": None
        }), 500


@factcheck_bp.route("/health", methods=["GET"])
def factcheck_health():
    """
    Health check endpoint for the fact-check service.
    
    Returns:
        200: {"status": "healthy", "service": "factcheck"}
    """
    return jsonify({
        "status": "success",
        "message": "Fact-check service is running",
        "data": {
            "service": "factcheck",
            "health": "healthy"
        }
    }), 200