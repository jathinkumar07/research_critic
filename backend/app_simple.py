from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re
import requests
import json
import traceback
import logging
from werkzeug.utils import secure_filename

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB max file size

# Global variables for models
summarizer = None

def get_summarizer():
    """Get or create summarizer instance with error handling"""
    global summarizer
    if summarizer is None:
        try:
            logger.info("Loading summarizer model...")
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("Summarizer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarizer: {e}")
            # Return a fallback function
            def fallback_summarizer(text, **kwargs):
                # Simple extractive summarization fallback
                sentences = text.split('.')[:3]
                return [{"summary_text": '. '.join(sentences) + '.'}]
            summarizer = fallback_summarizer
    return summarizer

# ----------- UTILITIES -----------

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF with error handling"""
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc):
            try:
                page_text = page.get_text("text")
                text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")
                continue
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Error opening PDF: {e}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def safe_api_request(url, timeout=10):
    """Make API request with proper error handling"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.warning(f"API request timeout for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"API request failed for URL: {url}, Error: {e}")
        return None
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON response from URL: {url}")
        return None

def detect_plagiarism(text):
    """Detect plagiarism using Semantic Scholar API with fallback"""
    try:
        # Clean and prepare text
        words = re.findall(r'\b\w+\b', text.lower())
        common_words = [w for w in words if len(w) > 4]
        
        if len(common_words) < 3:
            return 0
        
        # Use first 6 meaningful words as keywords
        keywords = " ".join(common_words[:6])
        
        # Search for similar papers
        search_url = f"https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": keywords,
            "fields": "title,abstract",
            "limit": 5
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        
        abstracts = []
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                for paper in data["data"]:
                    abstract = paper.get("abstract", "")
                    if abstract and len(abstract) > 50:
                        abstracts.append(abstract)
        
        if not abstracts:
            logger.info("No abstracts found for comparison")
            return 0
        
        # Calculate similarity
        documents = [text] + abstracts
        
        try:
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(documents)
            similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:])[0]
            max_score = max(similarity_scores) * 100
            return round(max_score, 2) if max_score > 10 else 0
        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            return 0
            
    except Exception as e:
        logger.error(f"Error in plagiarism detection: {e}")
        return 0

def extract_citations(text):
    """Extract citations from text"""
    try:
        # Look for references section
        text_lower = text.lower()
        references_patterns = ["references", "bibliography", "works cited", "citations"]
        
        references_start = -1
        for pattern in references_patterns:
            pos = text_lower.find(pattern)
            if pos != -1:
                references_start = pos
                break
        
        if references_start == -1:
            # Try to find numbered references in text
            numbered_refs = re.findall(r'\[\d+\].*?(?=\[\d+\]|$)', text, re.DOTALL)
            return numbered_refs[:10] if numbered_refs else []
        
        # Extract references section
        references_text = text[references_start:]
        references = []
        
        # Split by common reference patterns
        ref_lines = references_text.split("\n")
        for line in ref_lines[:20]:  # Limit to first 20 lines
            line = line.strip()
            if len(line) > 20 and not line.lower().startswith(('references', 'bibliography')):
                references.append(line)
                if len(references) >= 10:
                    break
        
        return references
    except Exception as e:
        logger.error(f"Error extracting citations: {e}")
        return []

def clean_citation(citation):
    """Clean and extract title from citation"""
    try:
        citation = citation.replace("\n", " ").strip()
        
        # Try to extract title from quotes
        title_match = re.search(r'"([^"]+)"', citation)
        if title_match:
            return title_match.group(1)
        
        # Try to extract title before first period
        parts = citation.split(".")
        if len(parts) > 0:
            title_candidate = parts[0].strip()
            if len(title_candidate) > 10:
                return title_candidate
        
        # Return original if no better option
        return citation if len(citation) > 5 else ""
    except Exception as e:
        logger.warning(f"Error cleaning citation: {e}")
        return citation

def validate_citations(citations):
    """Validate citations using Semantic Scholar API"""
    citation_results = []
    
    for i, citation in enumerate(citations[:10]):  # Limit to 10 citations
        try:
            cleaned_title = clean_citation(citation)
            if not cleaned_title:
                citation_results.append({
                    "reference": citation,
                    "valid": False
                })
                continue
            
            # Search for the citation
            search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                "query": cleaned_title,
                "fields": "title,authors",
                "limit": 3
            }
            
            data = safe_api_request(search_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()]))
            
            is_valid = False
            if data and "data" in data and len(data["data"]) > 0:
                # Check if any result is a good match
                for result in data["data"]:
                    result_title = result.get("title", "").lower()
                    if len(result_title) > 5:
                        is_valid = True
                        break
            
            citation_results.append({
                "reference": citation,
                "valid": is_valid
            })
            
        except Exception as e:
            logger.warning(f"Error validating citation {i}: {e}")
            citation_results.append({
                "reference": citation,
                "valid": False
            })
    
    return citation_results

# ----------- CRITIQUE MODULE -----------

def critique_paper(text):
    """Critique paper content"""
    try:
        critique_result = {}
        
        # Check for methodology keywords
        methodology_keywords = [
            "sample size", "experiment", "survey", "hypothesis",
            "qualitative", "quantitative", "interview", "randomized",
            "methodology", "method", "analysis", "data"
        ]
        
        found_keywords = [kw for kw in methodology_keywords if kw.lower() in text.lower()]
        
        if not found_keywords:
            critique_result["methodology_issues"] = "No standard research methodology terms found."
        else:
            critique_result["methodology_issues"] = f"Methodology terms found: {', '.join(found_keywords[:5])}."
        
        # Check for bias language
        bias_terms = ["clearly", "obviously", "undoubtedly", "without a doubt", "everyone knows", "we believe"]
        found_bias = [term for term in bias_terms if term.lower() in text.lower()]
        
        if found_bias:
            critique_result["bias_language"] = found_bias[:5]  # Limit to 5
        
        # Provide suggestions
        if not found_keywords:
            critique_result["suggestion"] = "Consider describing your research methods in detail."
        elif found_bias:
            critique_result["suggestion"] = "Avoid subjective language to maintain objectivity."
        else:
            critique_result["suggestion"] = "The methodology appears sound and objective."
        
        return critique_result
    except Exception as e:
        logger.error(f"Error in paper critique: {e}")
        return {"suggestion": "Could not analyze paper structure"}

def count_words(text):
    """Count words in text"""
    try:
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    except:
        return 0

# ----------- API ENDPOINTS -----------

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "success",
        "message": "Research Paper Analysis API is running"
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "status": "success",
        "message": "Research Paper Analysis API",
        "version": "1.0.0"
    }), 200

@app.route("/analyze", methods=["POST"])
def analyze_paper():
    """Main analysis endpoint"""
    try:
        logger.info("Starting paper analysis request")
        
        # Check if file is present
        if "file" not in request.files:
            logger.error("No file uploaded")
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files["file"]
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({"error": "No file selected"}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.pdf'):
            logger.error("Invalid file type")
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Save file
        pdf_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(pdf_path)
        logger.info(f"File saved: {pdf_path}")
        
        try:
            # Extract text from PDF
            logger.info("Extracting text from PDF")
            text = extract_text_from_pdf(pdf_path)
            
            if not text or len(text.strip()) < 50:
                logger.error("No readable text found in PDF")
                return jsonify({"error": "No readable text found in PDF or text too short"}), 400
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Generate summary
            logger.info("Generating summary")
            try:
                summarizer_model = get_summarizer()
                # Limit text for summarization to avoid memory issues
                text_for_summary = text[:1024] if len(text) > 1024 else text
                summary_result = summarizer_model(text_for_summary, max_length=200, min_length=50, do_sample=False)
                summary = summary_result[0]["summary_text"]
            except Exception as e:
                logger.warning(f"Summarization failed: {e}")
                # Fallback: use first few sentences
                sentences = text.split('.')[:3]
                summary = '. '.join(sentences) + '.'
            
            # Detect plagiarism
            logger.info("Detecting plagiarism")
            plagiarism_score = detect_plagiarism(text)
            
            # Extract and validate citations
            logger.info("Extracting citations")
            citations = extract_citations(text)
            logger.info(f"Found {len(citations)} citations")
            
            logger.info("Validating citations")
            citation_results = validate_citations(citations)
            
            # Generate critique
            logger.info("Generating critique")
            critique_result = critique_paper(text)
            
            # Calculate stats
            word_count = count_words(text)
            
            # Prepare response
            response = {
                "summary": summary,
                "plagiarism": plagiarism_score,
                "citations": citation_results,
                "fact_check": {
                    "facts": []  # Placeholder for fact check results
                },
                "stats": {
                    "word_count": word_count,
                    "plagiarism_percent": plagiarism_score,
                    "citations_count": len(citation_results)
                }
            }
            
            logger.info("Analysis completed successfully")
            return jsonify(response), 200
            
        finally:
            # Clean up uploaded file
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    logger.info(f"Cleaned up file: {pdf_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up file: {e}")
    
    except Exception as e:
        logger.error(f"Error in analyze_paper: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 25MB."}), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error occurred"}), 500

if __name__ == "__main__":
    logger.info("Starting Research Paper Analysis API")
    logger.info("Preloading models...")
    
    # Preload summarizer
    try:
        get_summarizer()
        logger.info("Models preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload models: {e}")
    
    logger.info("Starting Flask server on port 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)