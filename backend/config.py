import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR') or 'uploads'
    REPORT_DIR = os.environ.get('REPORT_DIR') or 'reports'
    CORPUS_DIR = os.environ.get('CORPUS_DIR') or 'corpus'
    MAX_UPLOAD_MB = int(os.environ.get('MAX_UPLOAD_MB', 25))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    ALLOWED_EXT = os.environ.get('ALLOWED_EXT', '.pdf')
    
    # API settings
    SEMANTIC_SCHOLAR_BASE = os.environ.get('SEMANTIC_SCHOLAR_BASE', 'https://api.semanticscholar.org/graph/v1/paper/search')
    SEMANTIC_SCHOLAR_FIELDS = os.environ.get('SEMANTIC_SCHOLAR_FIELDS', 'title,authors,year,venue')
    
    # Google Fact Check API
    GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
    GOOGLE_FACT_CHECK_URL = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
    
    # CrossRef API (no key required)
    CROSSREF_API_URL = 'https://api.crossref.org/works'
    
    # HuggingFace settings
    HF_MODEL_NAME = os.environ.get('HF_MODEL_NAME', 'facebook/bart-large-cnn')
    HF_CACHE_DIR = os.environ.get('HF_CACHE_DIR', './models_cache')
    
    # Feature flags
    USE_HF_SUMMARIZER = os.environ.get('USE_HF_SUMMARIZER', 'true').lower() == 'true'
    ALLOW_GUEST_UPLOADS = os.environ.get('ALLOW_GUEST_UPLOADS', 'false').lower() == 'true'
    
    # JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 30 * 24 * 3600  # 30 days
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
    
    # Security settings
    UPLOAD_FOLDER_PERMISSIONS = 0o755
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024  # Already defined above