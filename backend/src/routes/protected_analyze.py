from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os, tempfile, logging
from src.extensions import db
from src.models.user import User
from src.models.document import Document
from src.models.analysis import Analysis
from src.models.citation import Citation
from src.services.pdf_service import extract_text_and_meta
from src.services.summarizer_service import summarize
from src.services.plagiarism_service import check_plagiarism, check
from src.services.citations_service import validate as validate_citations
from src.services.factcheck_service import extract_claims, fact_check_claims
from src.utils.normalizers import (
    normalize_plagiarism_result,
    normalize_citations_result,
    normalize_factcheck_result,
    safe_call_service
)

logger = logging.getLogger(__name__)
protected_analyze_bp = Blueprint("protected_analyze", __name__, url_prefix="/api/analyze")

@protected_analyze_bp.route("/upload", methods=["POST"])
@jwt_required()
def analyze_and_save():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            text, word_count, title = extract_text_and_meta(temp_path)
            if not text or len(text.strip()) < 100:
                return jsonify({"error": "Document text too short"}), 400

            # Save doc
            document = Document(
                user_id=current_user_id,
                filename=file.filename,
                stored_path=temp_path,
                title=title or file.filename,
                extracted_text=text,
                word_count=word_count,
            )
            db.session.add(document)
            db.session.flush()

            # Run analysis with safe service calls and normalization
            try:
                summary = summarize(text)
            except Exception:
                summary = "Unable to generate summary."

            plagiarism_raw = safe_call_service(check_plagiarism, text)
            if plagiarism_raw is None:
                plagiarism_raw = safe_call_service(check, text)
            plagiarism_result = normalize_plagiarism_result(plagiarism_raw)

            citation_raw = safe_call_service(validate_citations, text)
            citation_results = normalize_citations_result(citation_raw)

            fact_check_results = []
            try:
                claims = extract_claims(text)
                if claims:
                    fact_check_raw = safe_call_service(fact_check_claims, claims)
                    fact_check_results = normalize_factcheck_result(fact_check_raw)
            except Exception as e:
                logger.warning(f"Fact check failed: {e}")
                fact_check_results = [{"claim": "Service unavailable", "status": "Unverified"}]

            # Save analysis
            analysis = Analysis(
                document_id=document.id,
                summary=summary,
                plagiarism_score=plagiarism_result.get("plagiarism_score", 0.0),
                plagiarism_details=plagiarism_result.get("matching_sources", []),
                fact_check_results=fact_check_results,
            )
            db.session.add(analysis)

            # Save citations
            for c in citation_results:
                citation = Citation(
                    analysis_id=analysis.id,
                    raw_text=str(c.get("reference", "")),
                    cleaned_title=str(c.get("reference", "")),
                    doi=c.get("doi"),
                    status="verified" if c.get("valid", False) else "unverified",
                )
                db.session.add(citation)

            db.session.commit()

            # Format response - ensure consistent structure
            formatted_citations = []
            for c in citation_results:
                formatted_citations.append({
                    "reference": str(c.get("reference", "Unknown")),
                    "valid": bool(c.get("valid", False))
                })

            formatted_facts = []
            for f in fact_check_results:
                formatted_facts.append({
                    "claim": str(f.get("claim", "Unknown claim")),
                    "status": str(f.get("status", "Unverified"))
                })

            response = {
                "analysis_id": analysis.id,
                "document_id": document.id,
                "summary": str(summary),
                "plagiarism": float(plagiarism_result.get("plagiarism_score", 0.0)),
                "plagiarism_details": list(plagiarism_result.get("matching_sources", [])),
                "citations": formatted_citations,
                "fact_check": {"facts": formatted_facts},
                "stats": {
                    "word_count": int(word_count),
                    "plagiarism_percent": float(plagiarism_result.get("plagiarism_score", 0.0)),
                    "citations_count": len(formatted_citations),
                    "fact_checks_count": len(formatted_facts),
                },
            }

            return jsonify(response), 200

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Analysis failed: {e}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@protected_analyze_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "protected_analyze",
        "message": "Protected analyze service is running",
    }), 200
