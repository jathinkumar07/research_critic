# AI Research Critic 📚🤖

A comprehensive full-stack application that analyzes research papers using AI-powered tools. Upload a PDF research paper and get instant analysis including plagiarism detection, citation validation, content summarization, and research critique.

> **📚 New to coding?** This README is designed for absolute beginners! Follow the step-by-step instructions and you'll have the app running in 10-15 minutes.

## 📋 What You'll Get After Setup

- ✅ A fully functional web application at `http://localhost:3000`
- ✅ AI-powered research paper analysis
- ✅ Beautiful, modern user interface
- ✅ Secure user authentication system
- ✅ Professional PDF report generation
- ✅ Works completely offline (graceful API fallbacks for basic functionality)

## ✨ What This Application Does

- **📄 PDF Analysis**: Upload research papers and extract text automatically
- **🤖 AI Summarization**: Get intelligent summaries of research content using HuggingFace models
- **🔍 Plagiarism Detection**: Check for content similarity and potential plagiarism (offline heuristic analysis)
- **📚 Citation Validation**: Verify citations and references (works offline with graceful API fallbacks)
- **✅ Fact Checking**: Validate claims using Google's Fact Check API (optional - works without API keys)
- **📊 Interactive Dashboard**: View results with beautiful charts and visualizations
- **📋 PDF Reports**: Generate professional analysis reports
- **🔐 User Authentication**: Secure login system with role-based access

## 🚀 Quick Start - Deployment Ready

**⏱️ Total Setup Time: 10-15 minutes**

### 📖 Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd research_paper_analysis-main/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 🗄️ Database Setup (PostgreSQL)

```bash
# Make sure PostgreSQL is running
# Create database
createdb researchdb

# Ensure your PostgreSQL credentials match the .env file:
# - User: postgres
# - Password: root
# - Database: researchdb
# - Host: localhost
# - Port: 5432
```

### ⚙️ Environment Setup

1. **Copy the .env configuration** (use exactly these values):

```bash
# =========================
# Flask Configuration
# =========================
FLASK_ENV=production
SECRET_KEY=7db4e3a1a3f94c8e8b73491f5c5c07d5b1e4f3b2fdbd48a7b6a2c0a3a9d3d45b
JWT_SECRET_KEY=4d91af09c8b9455da8f2f4e8b29e0c2e9b4a99dc63ff6b40c287d7c8a1d63b7f

# =========================
# Database Configuration (PostgreSQL)
# =========================
SQLALCHEMY_DATABASE_URI=postgresql://postgres:root@localhost:5432/researchdb

# =========================
# Upload and Storage Settings
# =========================
UPLOAD_DIR=uploads
REPORT_DIR=reports
CORPUS_DIR=corpus
MAX_UPLOAD_MB=25
ALLOWED_EXT=.pdf

# =========================
# API Settings
# =========================
SEMANTIC_SCHOLAR_BASE=https://api.semanticscholar.org/graph/v1/paper/search
SEMANTIC_SCHOLAR_FIELDS=title,authors,year,venue
CROSSREF_API_KEY=your-crossref-api-key-here   # placeholder, not real

# =========================
# Google Fact Check API (Optional)
# =========================
GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE=C:\Users\jathi\Downloads\research_paper_analysis-main mk9\research_paper_analysis-main\backend\fact_check_key.json
FACTCHECK_USE=service_account

# =========================
# Feature Flags
# =========================
USE_HF_SUMMARIZER=true
HF_MODEL_NAME=facebook/bart-large-cnn
HF_CACHE_DIR=./models_cache
ALLOW_GUEST_UPLOADS=false

# =========================
# JWT Settings
# =========================
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# =========================
# Security & CORS
# =========================
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Important Notes:**
- **No real API keys needed** for basic functionality - the app works with graceful fallbacks
- Only Google Fact Check uses a service account JSON file (optional)
- Semantic Scholar and CrossRef API keys are placeholders and not required

### 🚀 Run Flask Application

```bash
# Set environment variable for Google Fact Check (if available)
# Windows PowerShell:
$env:FACTCHECK_SERVICE_ACCOUNT="C:\path\to\fact_check_key.json"
# Mac/Linux:
export FACTCHECK_SERVICE_ACCOUNT="/path/to/fact_check_key.json"

# Run Flask
flask run
```

### 🌐 Upload PDFs and Test

1. Go to `http://127.0.0.1:5000`
2. Upload a PDF research paper
3. The app will:
   - Extract and summarize content using HuggingFace models
   - Check for plagiarism using offline heuristic analysis
   - Validate citations using local parsing (no external APIs required)
   - Attempt fact-checking with Google API (graceful fallback if unavailable)

## 🏗️ Deployment Notes

### For Production Deployment:

1. **Environment Configuration:**
   - Set `FLASK_ENV=production` in `.env`
   - Use strong, unique values for `SECRET_KEY` and `JWT_SECRET_KEY`
   - Configure your production PostgreSQL credentials in `SQLALCHEMY_DATABASE_URI`

2. **Optional API Services:**
   - **Google Fact Check**: Obtain a service account JSON file and set the path in `GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE`
   - **Semantic Scholar**: Get API key and replace placeholder in `SEMANTIC_SCHOLAR_API_KEY` 
   - **CrossRef**: Get API key and replace placeholder in `CROSSREF_API_KEY`

3. **Security:**
   - Keep Google FactCheck service account JSON file secure and private
   - Use environment variables for sensitive configuration
   - Configure proper CORS origins for your domain

4. **Storage:**
   - Ensure upload directories (`UPLOAD_DIR`, `REPORT_DIR`, `CORPUS_DIR`) are writable
   - Configure file size limits via `MAX_UPLOAD_MB`

## 🔧 Service Behavior

### Graceful API Fallbacks

The application is designed to work gracefully without external API keys:

- **Citation Validation**: Uses local text parsing and heuristic validation when API keys are missing
- **Fact Checking**: Returns "Unverified" status when Google API is unavailable
- **Plagiarism Detection**: Uses offline n-gram analysis (no external APIs required)
- **Summarization**: Uses local HuggingFace models (no external APIs required)

### Expected Output Formats

All services return normalized outputs:

- **Plagiarism**: `{"plagiarism_score": float, "matching_sources": list}`
- **Citations**: `list[{"reference": str, "valid": bool}]`
- **Fact Check**: `list[{"claim": str, "status": str}]`

## 🐛 Troubleshooting

### Common Issues:

1. **Database Connection Error**: Ensure PostgreSQL is running and credentials match `.env`
2. **Port Already in Use**: Change Flask port with `flask run --port 5001`
3. **Missing Dependencies**: Run `pip install -r requirements.txt` again
4. **API Errors**: Check logs - the app should gracefully handle missing API keys

### Testing Without API Keys:

The application is designed to work completely without external API keys. You should be able to:
- Upload PDFs successfully
- Get summaries via HuggingFace
- See plagiarism scores (offline analysis)
- View citation analysis (local parsing)
- Get "Unverified" fact-check results (graceful fallback)

## 📞 Support

If you encounter any issues:
1. Check the Flask logs for detailed error messages
2. Ensure all dependencies are installed
3. Verify database connectivity
4. Test with a small PDF file first

The application is built to be resilient and should never crash due to missing API keys or external service failures.

