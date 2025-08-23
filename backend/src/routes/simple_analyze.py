from flask import Blueprint, request, jsonify
import os, tempfile, logging
from src.services.pdf_service import extract_text_and_meta
from src.services.summarizer_service import summarize
from src.services.plagiarism_service import check_plagiarism, check
from src.services.citations_service import validate as validate_citations
from src.services.factcheck_service import extract_claims, fact_check_claims

logger = logging.getLogger(__name__)
simple_analyze_bp = Blueprint("simple_analyze", __name__, url_prefix="/api/simple")

# ------------------ Normalizers ------------------

def _norm_plagiarism(res):
    """Normalize plagiarism results to always return proper format."""
    if isinstance(res, dict):
        return {
            "plagiarism_score": float(res.get("plagiarism_score", 0.0)),
            "matching_sources": res.get("matching_sources", []) or []
        }
    if isinstance(res, (int, float)):
        v = float(res)
        if v > 1.0:  # treat as %
            v = v / 100.0
        return {"plagiarism_score": v, "matching_sources": []}
    return {"plagiarism_score": 0.0, "matching_sources": []}

def _norm_list_of_dicts(val):
    """Normalize list of dicts, ensuring each item is a dict."""
    if isinstance(val, list):
        return [x for x in val if isinstance(x, dict)]
    return []

def _norm_citation(c):
    """Normalize a single citation dict."""
    if not isinstance(c, dict):
        return {"reference": "Unknown", "valid": False}
    
    reference = c.get("raw") or c.get("cleaned_title") or c.get("reference") or "Unknown citation"
    valid = bool(c.get("valid", False))
    
    return {"reference": str(reference), "valid": valid}

def _norm_fact_check(f):
    """Normalize a single fact check dict."""
    if not isinstance(f, dict):
        return {"claim": "Unknown claim", "status": "Unverified"}
    
    claim = f.get("claim") or "Unknown claim"
    status_raw = f.get("status", "no_verdict")
    
    # Map status to user-friendly format
    status_map = {
        "verified": "Verified",
        "contradicted": "Contradicted", 
        "no_verdict": "Unverified",
        "api_error": "Unverified"
    }
    status = status_map.get(status_raw, "Unverified")
    
    return {"claim": str(claim), "status": status}

# ------------------ Routes ------------------

@simple_analyze_bp.route("/upload", methods=["POST"])
def analyze_document():
    try:
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
            # Extract text
            text, word_count, title = extract_text_and_meta(temp_path)
            if not text or len(text.strip()) < 100:
                return jsonify({"error": "Document text too short"}), 400

            # Run analysis
            logger.info("Running summarization...")
            try:
                summary = summarize(text)
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                summary = "Unable to generate summary."

            logger.info("Running plagiarism check...")
            try:
                plagiarism_result = check_plagiarism(text)
            except Exception:
                plagiarism_result = check(text)
            plagiarism_result = _norm_plagiarism(plagiarism_result)

            logger.info("Validating citations...")
            try:
                citation_results = validate_citations(text)
            except Exception:
                citation_results = []
            citation_results = _norm_list_of_dicts(citation_results)

            logger.info("Running fact check...")
            try:
                claims = extract_claims(text)
                fact_check_results = fact_check_claims(claims) if claims else []
            except Exception:
                fact_check_results = []
            fact_check_results = _norm_list_of_dicts(fact_check_results)

            # Format for frontend
            formatted_citations = [_norm_citation(c) for c in citation_results]

            formatted_facts = [_norm_fact_check(f) for f in fact_check_results]

            return jsonify({
                "summary": summary,
                "plagiarism": plagiarism_result["plagiarism_score"],
                "plagiarism_details": plagiarism_result["matching_sources"],
                "citations": formatted_citations,
                "fact_check": {"facts": formatted_facts},
                "stats": {
                    "word_count": word_count,
                    "plagiarism_percent": plagiarism_result["plagiarism_score"],
                    "citations_count": len(formatted_citations),
                    "fact_checks_count": len(formatted_facts),
                }
            }), 200

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Simple analysis failed: {e}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
