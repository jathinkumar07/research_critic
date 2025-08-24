from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from transformers import pipeline
import os
import re
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global model cache
_summarizer = None

def get_summarizer():
    """Get or initialize the summarizer model."""
    global _summarizer
    if _summarizer is None:
        logger.info("Loading summarizer model...")
        _summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        logger.info("Summarizer model loaded successfully")
    return _summarizer

# ----------- PDF PROCESSING -----------

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""

def get_word_count(text: str) -> int:
    """Get word count from text."""
    return len(re.findall(r'\b\w+\b', text))

def get_document_title(text: str) -> str:
    """Extract document title from text (first meaningful line)."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:10]:  # Check first 10 lines
        if len(line) > 10 and len(line) < 200:  # Reasonable title length
            return line
    return "Untitled Document"

# ----------- PLAGIARISM DETECTION -----------

def detect_plagiarism_advanced(text: str) -> Dict[str, Any]:
    """
    Advanced plagiarism detection combining multiple methods:
    1. Semantic Scholar API search
    2. Internal repetition analysis
    3. TF-IDF similarity scoring
    """
    if not text or len(text) < 200:
        return {"plagiarism_score": 0.0, "matching_sources": [], "details": "Text too short for analysis"}
    
    # Method 1: External similarity check (from your working demo)
    external_score = detect_external_similarity(text)
    
    # Method 2: Internal repetition analysis
    internal_score = detect_internal_repetition(text)
    
    # Combine scores (weighted average)
    combined_score = (external_score * 0.7 + internal_score * 0.3)
    
    return {
        "plagiarism_score": round(combined_score, 2),
        "matching_sources": [],
        "details": f"External similarity: {external_score}%, Internal repetition: {internal_score}%"
    }

def detect_external_similarity(text: str) -> float:
    """Detect similarity with external sources using Semantic Scholar API."""
    try:
        # Extract keywords for search
        words = re.findall(r'\b\w+\b', text.lower())
        common_words = [w for w in words if len(w) > 4]
        keywords = " ".join(common_words[:6])
        
        # Search Semantic Scholar
        search_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={keywords}&fields=title,abstract&limit=5"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Semantic Scholar API error: {response.status_code}")
            return 0.0
            
        data = response.json()
        
        abstracts = []
        if "data" in data:
            for paper in data["data"]:
                abstract = paper.get("abstract", "")
                if abstract:
                    abstracts.append(abstract)
        
        if not abstracts:
            return 0.0
            
        # Calculate TF-IDF similarity
        documents = [text] + abstracts
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
        max_score = max(similarity_scores) * 100
        
        return round(max_score, 2) if max_score > 10 else 0.0
        
    except requests.exceptions.Timeout:
        logger.warning("Semantic Scholar API timeout")
        return 0.0
    except Exception as e:
        logger.error(f"External similarity detection failed: {e}")
        return 0.0

def detect_internal_repetition(text: str) -> float:
    """Detect internal repetition using n-gram analysis."""
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
        
        if len(sentences) < 5:
            return 0.0
        
        # Create 7-grams for each sentence
        all_ngrams = []
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            if len(words) >= 7:
                ngrams = [' '.join(words[i:i+7]) for i in range(len(words) - 6)]
                all_ngrams.extend(ngrams)
        
        if not all_ngrams:
            return 0.0
        
        # Count duplicates
        from collections import Counter
        ngram_counts = Counter(all_ngrams)
        duplicates = sum(count for count in ngram_counts.values() if count > 1)
        total = len(all_ngrams)
        
        repetition_score = (duplicates / max(1, total)) * 100
        return min(100.0, repetition_score)
        
    except Exception as e:
        logger.error(f"Internal repetition detection failed: {e}")
        return 0.0

# ----------- CITATION VALIDATION -----------

def extract_citations(text: str) -> List[str]:
    """Extract citations from the references section."""
    try:
        # Find references section
        references_start = text.lower().find("references")
        if references_start == -1:
            references_start = text.lower().find("bibliography")
        if references_start == -1:
            return []
        
        references_text = text[references_start:]
        
        # Split by lines and clean
        references = []
        lines = references_text.split("\n")
        
        for line in lines[1:]:  # Skip the "References" header
            line = line.strip()
            if len(line) > 20:  # Minimum length for a citation
                references.append(line)
            if len(references) >= 20:  # Limit to first 20 citations
                break
        
        return references
        
    except Exception as e:
        logger.error(f"Citation extraction failed: {e}")
        return []

def clean_citation(citation: str) -> str:
    """Clean citation text to extract the main title."""
    citation = citation.replace("\n", " ").strip()
    
    # Try to extract title from quotes
    title_match = re.search(r'"([^"]+)"', citation)
    if title_match:
        return title_match.group(1)
    
    # Try to extract title before first period
    title_candidate = citation.split(".")[0]
    if len(title_candidate) > 5:
        return title_candidate
    
    return citation

def validate_citations(citations: List[str]) -> Dict[str, str]:
    """Validate citations using Semantic Scholar API."""
    citation_results = {}
    
    for citation in citations[:10]:  # Limit to first 10 citations
        try:
            cleaned_title = clean_citation(citation)
            
            # Try full citation first
            result = search_citation(citation)
            if result != "Not Found":
                citation_results[citation] = result
                continue
            
            # Try cleaned title
            result = search_citation(cleaned_title)
            if result != "Not Found":
                citation_results[citation] = result
                continue
            
            # Try keywords from title
            keywords = " ".join(cleaned_title.split()[:4])
            result = search_citation(keywords)
            citation_results[citation] = result
            
        except Exception as e:
            logger.error(f"Citation validation error for '{citation}': {e}")
            citation_results[citation] = f"Error: {str(e)}"
    
    return citation_results

def search_citation(query: str) -> str:
    """Search for a citation using Semantic Scholar API."""
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&fields=title,authors"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0]["title"]
        
        return "Not Found"
        
    except requests.exceptions.Timeout:
        return "API Timeout"
    except Exception as e:
        return f"API Error: {str(e)}"

# ----------- CRITIQUE MODULE -----------

def critique_paper(text: str) -> Dict[str, Any]:
    """Provide critique and suggestions for the research paper."""
    critique_result = {}
    
    # Check for methodology terms
    methodology_keywords = [
        "sample size", "experiment", "survey", "hypothesis",
        "qualitative", "quantitative", "interview", "randomized",
        "methodology", "method", "approach", "data collection"
    ]
    found_keywords = [kw for kw in methodology_keywords if kw.lower() in text.lower()]
    
    if not found_keywords:
        critique_result["methodology_issues"] = "No standard research methodology terms found. Consider describing your research methods in detail."
    else:
        critique_result["methodology_issues"] = f"Methodology terms found: {', '.join(found_keywords)}. Good methodological foundation."
    
    # Check for bias language
    bias_terms = ["clearly", "obviously", "undoubtedly", "without a doubt", "everyone knows", "we believe", "it is obvious"]
    found_bias = [term for term in bias_terms if term.lower() in text.lower()]
    
    if found_bias:
        critique_result["bias_language"] = f"Potentially biased language detected: {', '.join(found_bias[:3])}. Consider using more objective language."
    else:
        critique_result["bias_language"] = "Language appears objective and unbiased."
    
    # Check for statistical terms
    stats_terms = ["p-value", "significance", "correlation", "regression", "statistical", "significant"]
    found_stats = [term for term in stats_terms if term.lower() in text.lower()]
    
    if found_stats:
        critique_result["statistical_rigor"] = f"Statistical terms found: {', '.join(found_stats)}. Good statistical foundation."
    else:
        critique_result["statistical_rigor"] = "Limited statistical analysis detected. Consider adding statistical validation."
    
    # Overall suggestion
    if not found_keywords and found_bias:
        critique_result["suggestion"] = "Improve methodology description and reduce subjective language."
    elif not found_keywords:
        critique_result["suggestion"] = "Consider describing your research methods in more detail."
    elif found_bias:
        critique_result["suggestion"] = "Avoid subjective language to maintain objectivity."
    else:
        critique_result["suggestion"] = "The methodology appears sound and objective. Good work!"
    
    return critique_result

# ----------- API ENDPOINTS -----------

@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "status": "success",
        "message": "AI Research Critic API - Improved Version",
        "data": {
            "version": "2.0.0",
            "service": "ai_research_critic_improved",
            "endpoints": {
                "analyze": "/analyze (POST) - Analyze PDF document",
                "health": "/health (GET) - Health check"
            }
        }
    }), 200

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "success",
        "message": "AI Research Critic API is running",
        "data": {
            "service": "ai_research_critic_improved",
            "health": "healthy",
            "model_loaded": _summarizer is not None
        }
    }), 200

@app.route("/analyze", methods=["POST"])
def analyze_paper():
    """Main analysis endpoint for PDF documents."""
    try:
        # Validate file upload
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            # Extract text from PDF
            logger.info("Extracting text from PDF...")
            text = extract_text_from_pdf(temp_path)
            
            if not text or len(text.strip()) < 100:
                return jsonify({"error": "No readable text found in PDF or document too short"}), 400

            # Get document metadata
            word_count = get_word_count(text)
            title = get_document_title(text)
            
            logger.info(f"Processing document: {title} ({word_count} words)")

            # Run analysis
            logger.info("Generating summary...")
            try:
                summarizer = get_summarizer()
                # Limit text for summarization to avoid token limits
                summary_text = text[:1024] if len(text) > 1024 else text
                summary = summarizer(summary_text, max_length=200, min_length=50, do_sample=False)[0]["summary_text"]
            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                summary = "Unable to generate summary due to processing limitations."

            logger.info("Detecting plagiarism...")
            plagiarism_result = detect_plagiarism_advanced(text)

            logger.info("Extracting and validating citations...")
            citations = extract_citations(text)
            citation_results = validate_citations(citations)

            logger.info("Generating critique...")
            critique_result = critique_paper(text)

            # Format citations for frontend
            formatted_citations = []
            for citation_text, result in citation_results.items():
                formatted_citations.append({
                    "reference": citation_text,
                    "valid": result != "Not Found" and not result.startswith("Error") and result != "API Timeout"
                })
            
            # Format response to match frontend expectations
            response = {
                "summary": summary,
                "plagiarism": plagiarism_result.get("plagiarism_score", 0.0),
                "citations": formatted_citations,
                "fact_check": {
                    "facts": []  # Placeholder for fact checking functionality
                },
                "stats": {
                    "word_count": word_count,
                    "plagiarism_percent": plagiarism_result.get("plagiarism_score", 0.0),
                    "citations_count": len(formatted_citations)
                }
            }

            logger.info("Analysis completed successfully")
            return jsonify(response), 200

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({
            "status": "error",
            "error": f"Analysis failed: {str(e)}"
        }), 500

# ----------- APPLICATION STARTUP -----------

if __name__ == "__main__":
    print("🚀 Starting AI Research Critic - Improved Version")
    print("📋 Preloading models...")
    
    # Preload the summarizer model
    try:
        get_summarizer()
        print("✅ Models loaded successfully")
    except Exception as e:
        print(f"⚠️ Warning: Model preloading failed: {e}")
    
    print("🌐 Starting Flask server...")
    app.run(debug=False, host='0.0.0.0', port=5000)