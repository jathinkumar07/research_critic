from flask import Blueprint, request, jsonify
from src.services.citations_service import validate
from src.services.pdf_service import extract_text_and_meta
from src.models.document import Document

citations_bp = Blueprint("citations", __name__)


@citations_bp.route("/validate", methods=["POST"])
def validate_citations_endpoint():
    """
    Validate a list of citations or extract them from text / document.
    """
    try:
        payload = request.get_json(force=True, silent=True) or {}
        citations_data = None
        source_type = None

        # 1️⃣ Direct citations list
        if "citations" in payload:
            citations_list = payload.get("citations")
            if not isinstance(citations_list, list):
                return jsonify({"status": "error", "message": "citations must be a list", "data": None}), 400
            if not citations_list:
                return jsonify({"status": "success", "message": "No citations provided", "data": _empty_response()}), 200

            # Clean each citation before validating
            cleaned_list = [str(c).strip() for c in citations_list]
            # Use the validate function with concatenated citations
            citations_text = "\n".join(cleaned_list)
            citations_data = validate(citations_text)
            source_type = "citations_list"

        # 2️⃣ From document_id
        elif "document_id" in payload:
            doc_id = payload.get("document_id")
            if not isinstance(doc_id, int):
                return jsonify({"status": "error", "message": "document_id must be integer", "data": None}), 400

            document = Document.query.get(doc_id)
            if not document:
                return jsonify({"status": "error", "message": "document not found", "data": None}), 404

            text, word_count, title = extract_text_and_meta(document.stored_path)
            if not text or len(text.strip()) < 100:
                return jsonify({"status": "error", "message": "Document too short", "data": None}), 400

            citations_data = validate(text)
            source_type = "document"

        # 3️⃣ From raw text
        elif "text" in payload:
            text = payload.get("text")
            if not isinstance(text, str):
                return jsonify({"status": "error", "message": "text must be string", "data": None}), 400
            if not text or len(text.strip()) < 100:
                return jsonify({"status": "error", "message": "Text too short", "data": None}), 400

            citations_data = validate(text)
            source_type = "text"

        else:
            return jsonify({"status": "error", "message": "Provide citations, document_id or text", "data": None}), 400

        # 4️⃣ If nothing found
        if not citations_data:
            return jsonify({"status": "success", "message": "No citations found", "data": _empty_response()}), 200

        # 5️⃣ Count valid/invalid
        valid_count = sum(1 for c in citations_data if c.get("status", "").lower() == "valid")
        invalid_count = len(citations_data) - valid_count

        # 6️⃣ Determine source API
        from src.services.citations_service import CROSSREF_API_KEY, SEMANTIC_SCHOLAR_KEY
        if SEMANTIC_SCHOLAR_KEY:
            api_source = "semantic_scholar"
        elif CROSSREF_API_KEY:
            api_source = "crossref"
        else:
            api_source = "mock"

        return jsonify({
            "status": "success",
            "message": f"Validated {len(citations_data)} citations",
            "data": {
                "citations": citations_data,
                "total_citations": len(citations_data),
                "valid_count": valid_count,
                "invalid_count": invalid_count,
                "source": api_source
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Internal error: {str(e)}", "data": None}), 500


@citations_bp.route("/health", methods=["GET"])
def citations_health():
    """
    Health check endpoint for the citations service.
    """
    from src.services.citations_service import CROSSREF_API_KEY, SEMANTIC_SCHOLAR_KEY
    configured_apis = []
    if CROSSREF_API_KEY:
        configured_apis.append("CrossRef")
    if SEMANTIC_SCHOLAR_KEY:
        configured_apis.append("Semantic Scholar")

    return jsonify({
        "status": "success",
        "message": "Citations service is running",
        "data": {
            "service": "citations",
            "health": "healthy",
            "configured_apis": configured_apis,
            "fallback_mode": len(configured_apis) == 0
        }
    }), 200


def _empty_response():
    return {
        "citations": [],
        "total_citations": 0,
        "valid_count": 0,
        "invalid_count": 0,
        "source": "none"
    }
