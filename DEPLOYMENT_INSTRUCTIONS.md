# AI Research Critic - Deployment Instructions

## 🚀 Quick Start Guide

This guide provides step-by-step instructions to deploy and run the AI Research Critic application that analyzes PDF documents for plagiarism, citations, and provides research critique.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB (8GB+ recommended for better performance)
- **Storage**: At least 2GB free space for models and dependencies
- **Internet Connection**: Required for API calls and model downloads

### Required Python Packages
The application uses these main dependencies:
- Flask (web framework)
- PyMuPDF (PDF processing)
- Transformers (AI models)
- scikit-learn (text analysis)
- requests (API calls)

## 🛠️ Installation Steps

### Step 1: Clone/Download the Project
```bash
# If using git
git clone <repository-url>
cd ai-research-critic

# Or download and extract the project files
```

### Step 2: Set Up Python Environment

#### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Option B: System-wide Installation
```bash
# If you prefer system-wide installation (not recommended for production)
pip install --user -r requirements.txt
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter permission issues on some systems:
pip install --break-system-packages -r requirements.txt

# Or install manually:
pip install flask flask-cors PyMuPDF transformers scikit-learn requests python-dotenv
```

### Step 4: Verify Installation
```bash
# Navigate to backend directory
cd backend

# Test the application components
python3 -c "
import fitz
import transformers
import sklearn
from flask import Flask
print('✅ All dependencies installed successfully!')
"
```

## 🏃‍♂️ Running the Application

### Method 1: Using the Improved Standalone App (Recommended)

This is the best version that combines all working features from your demo:

```bash
# Navigate to backend directory
cd backend

# Start the server
python3 app_improved.py
```

**Expected Output:**
```
🚀 Starting AI Research Critic - Improved Version
📋 Preloading models...
INFO:__main__:Loading summarizer model...
Device set to use cpu
INFO:__main__:Summarizer model loaded successfully
✅ Models loaded successfully
🌐 Starting Flask server...
 * Serving Flask app 'app_improved'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[::1]:5000
```

### Method 2: Using the Modular App Structure

If you prefer the modular structure (requires additional setup):

```bash
# Install additional dependencies
pip install flask-sqlalchemy flask-migrate flask-jwt-extended

# Navigate to backend directory
cd backend

# Start the server
python3 app.py
```

## 🧪 Testing the Application

### Test 1: Health Check
```bash
# Test if the server is running
curl -X GET http://localhost:5000/health

# Expected response:
{
  "status": "success",
  "message": "AI Research Critic API is running",
  "data": {
    "service": "ai_research_critic_improved",
    "health": "healthy",
    "model_loaded": true
  }
}
```

### Test 2: API Information
```bash
# Get API information
curl -X GET http://localhost:5000/

# Expected response:
{
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
}
```

### Test 3: PDF Analysis
```bash
# Test with a sample PDF (make sure you have a PDF file)
curl -X POST -F "file=@uploads/sample.pdf" http://localhost:5000/analyze

# Or use the provided test script
python3 test_server.py
```

### Test 4: Using the Automated Test Script
```bash
# Run comprehensive tests
python3 test_server.py
```

**Expected Test Output:**
```
🧪 Testing AI Research Critic API
==================================================
1. Testing health endpoint...
✅ Health check passed

2. Testing root endpoint...
✅ Root endpoint working

3. Testing PDF analysis...
   Testing with: uploads/EJ1172284.pdf
✅ PDF analysis successful
   Document: The EUROCALL Review, Volume 25, No. 2, September...
   Word count: 7234
   Plagiarism score: 0.0%
   Citations found: 20
   Summary: This study examines the role of autonomous learning...

🎉 API testing completed!
```

## 📁 File Structure

```
ai-research-critic/
├── backend/
│   ├── app_improved.py          # ⭐ Main improved application (USE THIS)
│   ├── app.py                   # Modular version (complex setup)
│   ├── test_server.py           # Test script
│   ├── uploads/                 # PDF files for testing
│   │   ├── sample.pdf
│   │   └── EJ1172284.pdf
│   └── src/                     # Modular components (optional)
├── requirements.txt             # Python dependencies
└── DEPLOYMENT_INSTRUCTIONS.md   # This file
```

## 🔧 API Usage

### Analyze PDF Document

**Endpoint:** `POST /analyze`

**Request:**
```bash
curl -X POST \
  -F "file=@your_document.pdf" \
  http://localhost:5000/analyze
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "document_info": {
      "title": "Research Paper Title",
      "word_count": 5420,
      "pages_processed": "N/A"
    },
    "summary": "This paper discusses...",
    "plagiarism_score": 15.23,
    "plagiarism_details": "External similarity: 12.5%, Internal repetition: 18.7%",
    "citations": {
      "Smith, J. (2020). Research Methods...": "Research Methods in Social Sciences",
      "Doe, A. (2019). Data Analysis...": "Not Found"
    },
    "critique": {
      "methodology_issues": "Methodology terms found: experiment, survey, hypothesis. Good methodological foundation.",
      "bias_language": "Language appears objective and unbiased.",
      "statistical_rigor": "Statistical terms found: p-value, significance. Good statistical foundation.",
      "suggestion": "The methodology appears sound and objective. Good work!"
    }
  }
}
```

## 🔍 Features Verification

### ✅ PDF Processing
- **Text Extraction**: Uses PyMuPDF for robust PDF text extraction
- **Document Analysis**: Extracts title, word count, and metadata
- **Error Handling**: Graceful handling of corrupted or unreadable PDFs

### ✅ Plagiarism Detection
- **External Similarity**: Compares against Semantic Scholar database
- **Internal Repetition**: Detects self-plagiarism using n-gram analysis
- **Combined Scoring**: Weighted combination of multiple detection methods
- **Realistic Scores**: Provides meaningful plagiarism percentages

### ✅ Citation Validation
- **Reference Extraction**: Finds citations in References/Bibliography sections
- **API Validation**: Validates citations against Semantic Scholar API
- **Multiple Attempts**: Tries different search strategies for better results
- **Detailed Results**: Shows which citations are found/validated

### ✅ Research Critique
- **Methodology Assessment**: Checks for research methodology terms
- **Bias Detection**: Identifies potentially biased language
- **Statistical Rigor**: Evaluates statistical analysis presence
- **Constructive Suggestions**: Provides actionable improvement recommendations

## 🚨 Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors
```bash
# Make sure you're in the right directory and have installed dependencies
cd backend
pip install -r ../requirements.txt
```

#### 2. "Port already in use" error
```bash
# Kill existing processes
pkill -f python3
# Or use a different port
# Edit app_improved.py and change port=5000 to port=5001
```

#### 3. Model loading issues
```bash
# Check internet connection for model download
# Clear cache if needed
rm -rf ~/.cache/huggingface/
```

#### 4. PDF processing errors
- Ensure PDF files are not corrupted
- Check file permissions
- Verify PDF contains extractable text (not just images)

#### 5. API timeout issues
- Increase timeout values in code if needed
- Check internet connection for external API calls

## 🌐 Production Deployment

### For Production Use:

1. **Use a production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_improved:app
```

2. **Set up reverse proxy (nginx):**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. **Environment variables:**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
```

## 🎯 Performance Notes

- **First Request**: May take 30-60 seconds due to model loading
- **Subsequent Requests**: Much faster (2-10 seconds depending on document size)
- **Memory Usage**: ~2-4GB RAM during operation
- **Concurrent Users**: Single-threaded by default, use gunicorn for production

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Test with the provided sample PDFs first
4. Check internet connectivity for API calls

---

## ✨ Summary

**To get started quickly:**

1. Install dependencies: `pip install flask flask-cors PyMuPDF transformers scikit-learn requests`
2. Navigate to backend: `cd backend`
3. Run the app: `python3 app_improved.py`
4. Test: `curl -X GET http://localhost:5000/health`
5. Upload PDF: `curl -X POST -F "file=@uploads/sample.pdf" http://localhost:5000/analyze`

The application is now ready to analyze PDFs for plagiarism, validate citations, and provide research critique!