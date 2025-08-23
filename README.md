# AI Research Critic 📚🤖

A comprehensive full-stack application that analyzes research papers using AI-powered tools. Upload a PDF research paper and get instant analysis including plagiarism detection, citation validation, content summarization, and research critique.

> **📚 New to coding?** This README is designed for absolute beginners! Follow the step-by-step instructions and you'll have the app running in 10-15 minutes.

## 📋 What You'll Get After Setup

- ✅ A fully functional web application at `http://localhost:3000`
- ✅ AI-powered research paper analysis
- ✅ Beautiful, modern user interface
- ✅ Secure user authentication system
- ✅ Professional PDF report generation
- ✅ Works completely offline (no API keys required for basic functionality)
- ✅ Graceful fallbacks when external APIs are unavailable

## ✨ What This Application Does

- **📄 PDF Analysis**: Upload research papers and extract text automatically
- **🤖 AI Summarization**: Get intelligent summaries of research content
- **🔍 Plagiarism Detection**: Check for content similarity and potential plagiarism
- **📚 Citation Validation**: Verify citations using academic databases
- **✅ Fact Checking**: Validate claims using Google's Fact Check API
- **📊 Interactive Dashboard**: View results with beautiful charts and visualizations
- **📋 PDF Reports**: Generate professional analysis reports
- **🔐 User Authentication**: Secure login system with role-based access

## 🚀 Quick Start for Beginners

**⏱️ Total Setup Time: 10-15 minutes**

### 🎯 Super Quick Setup (Automated)

For Mac and Linux users, you can use our automated setup script:

```bash
# Make setup script executable and run it
chmod +x setup.sh
./setup.sh
```

For Windows users:
```cmd
setup.bat
```

**Or follow the detailed manual steps below** ⬇️

### 📖 Manual Setup Instructions

Follow these steps exactly, and you'll have the application running successfully!

## 📋 Prerequisites

Before you start, you need to install these tools on your computer:

### For Windows Users:

1. **Install Python 3.10 or higher**
   - Go to [python.org](https://www.python.org/downloads/)
   - Download Python 3.10+ for Windows
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation: Open Command Prompt and type `python --version`

2. **Install Node.js 16 or higher**
   - Go to [nodejs.org](https://nodejs.org/)
   - Download the LTS version for Windows
   - Install with default settings
   - Verify installation: Open Command Prompt and type `node --version`

3. **Install Git**
   - Go to [git-scm.com](https://git-scm.com/download/win)
   - Download and install with default settings

4. **Install PostgreSQL (Optional but Recommended)**
   - Go to [postgresql.org](https://www.postgresql.org/download/windows/)
   - Download and install PostgreSQL
   - Remember the password you set for the `postgres` user
   - Default settings are fine

### For Mac Users:

1. **Install Python 3.10 or higher**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.10
   
   # Or download from python.org
   ```

2. **Install Node.js 16 or higher**
   ```bash
   # Using Homebrew
   brew install node
   
   # Or download from nodejs.org
   ```

3. **Install Git** (usually pre-installed)
   ```bash
   git --version
   ```

4. **Install PostgreSQL (Optional but Recommended)**
   ```bash
   # Using Homebrew
   brew install postgresql
   brew services start postgresql
   ```

### For Linux Users:

1. **Install Python 3.10 or higher**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.10 python3.10-pip python3.10-venv
   
   # CentOS/RHEL/Fedora
   sudo dnf install python3.10 python3-pip
   ```

2. **Install Node.js 16 or higher**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # CentOS/RHEL/Fedora
   sudo dnf install nodejs npm
   ```

3. **Install Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git
   
   # CentOS/RHEL/Fedora
   sudo dnf install git
   ```

4. **Install PostgreSQL (Optional but Recommended)**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   
   # CentOS/RHEL/Fedora
   sudo dnf install postgresql postgresql-server
   sudo postgresql-setup --initdb
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

## 📥 Step 1: Download the Project

1. **Open Terminal/Command Prompt**
   - Windows: Press `Win + R`, type `cmd`, press Enter
   - Mac: Press `Cmd + Space`, type "Terminal", press Enter
   - Linux: Press `Ctrl + Alt + T`

2. **Navigate to where you want to save the project**
   ```bash
   # Example: Go to Desktop
   cd Desktop
   
   # Or create a new folder
   mkdir my-projects
   cd my-projects
   ```

3. **Clone the repository**
   ```bash
   git clone <YOUR_REPOSITORY_URL>
   cd research_paper_analysis-main
   ```

## ⚙️ Step 2: Backend Setup (Python/Flask)

### 2.1 Navigate to Backend Directory
```bash
cd backend
```

### 2.2 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

**✅ You'll know it worked when you see `(venv)` at the beginning of your command prompt**

### 2.3 Install Python Dependencies
```bash
pip install -r requirements.txt
```

**⏳ This may take 2-5 minutes depending on your internet speed**

### 2.4 Database Setup (PostgreSQL)

If you installed PostgreSQL, set up the database:

```bash
# Create the database
createdb researchdb

# Or if you need to specify user/password:
createdb -U postgres -h localhost researchdb
```

**Note**: The default configuration expects:
- Username: `postgres`
- Password: `root`
- Database: `researchdb`
- Host: `localhost`
- Port: `5432`

If your setup is different, update the `.env` file accordingly.

### 2.5 Environment Setup

Copy the example environment file and configure it:

```bash
# Copy the example environment file
cp .env.example .env
```

The `.env` file should contain exactly these values (as provided):

```env
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
# Google Fact Check API
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
- The API keys are placeholders and will work with graceful fallbacks
- Only Google Fact Check requires a service account JSON file
- The app will work without any real API keys

### 2.6 Initialize Database
```bash
# Initialize database migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations to create tables
flask db upgrade
```

### 2.7 Start Backend Server
```bash
# Set the Google Fact Check service account path (Windows)
$env:FACTCHECK_SERVICE_ACCOUNT="C:\path\to\fact_check_key.json"

# Start Flask
flask run
```

**✅ Success!** You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

**Keep this terminal window open** - this is your backend server running.

## 🎨 Step 3: Frontend Setup (React/TypeScript)

### 3.1 Open New Terminal Window
Keep the backend running and open a **new** terminal window/tab.

### 3.2 Navigate to Frontend Directory
```bash
# From the project root directory
cd frontend
```

### 3.3 Install Node.js Dependencies
```bash
npm install
```

**⏳ This may take 1-3 minutes**

### 3.4 Create Frontend Environment File

Create a `.env` file in the `frontend` directory:

```bash
# Create .env file (Windows)
echo. > .env

# Create .env file (Mac/Linux)
touch .env
```

Add this content to the `.env` file:

```env
# Backend API URL
REACT_APP_API_URL=http://127.0.0.1:5000
```

### 3.5 Start Frontend Server
```bash
npm start
```

**✅ Success!** Your browser should automatically open to `http://localhost:3000`

If it doesn't open automatically, manually go to: `http://localhost:3000`

## 🎉 Step 4: Test the Application

1. **Open your browser** to `http://localhost:3000`
2. **Register a new account** or login
3. **Upload a PDF research paper**
4. **Wait for analysis** to complete
5. **View the results** in the dashboard

## 🔑 API Keys Setup (Optional but Recommended)

The application works completely without API keys, but you can enhance functionality by adding real ones:

### Google Fact Check API (Most Important)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable "Fact Check Tools API"
4. Create a service account and download the JSON key file
5. Update the `GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE` path in `.env`

### Semantic Scholar API (Optional)
1. Go to [Semantic Scholar](https://api.semanticscholar.org)
2. Register for a free API key
3. Add `SEMANTIC_SCHOLAR_KEY=your_key_here` to `.env`

### CrossRef API (Optional)
1. Go to [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
2. Register for a free API key
3. Add `CROSSREF_API_KEY=your_key_here` to `.env`

## 🚀 Deployment Notes

For production deployment:

1. **Set `FLASK_ENV=production`** in your `.env` file
2. **Use proper PostgreSQL credentials** instead of the default ones
3. **Keep your Google Fact Check service account JSON safe** and secure
4. **Update CORS_ORIGINS** to include your production domain
5. **Use a proper WSGI server** like Gunicorn instead of Flask's development server

## 🛠️ Troubleshooting

### Common Issues:

1. **"Analysis failed: 'str' object has no attribute 'get'"**
   - ✅ **FIXED**: The code now handles missing API keys gracefully
   - The app will show placeholder results instead of crashing

2. **Database connection errors**
   - Make sure PostgreSQL is running
   - Check your database credentials in `.env`
   - Try: `sudo systemctl start postgresql` (Linux)

3. **Port already in use**
   - Kill the process using the port: `lsof -ti:5000 | xargs kill -9`
   - Or use a different port: `flask run --port=5001`

4. **Module not found errors**
   - Make sure you're in the virtual environment: `(venv)` should be visible
   - Reinstall dependencies: `pip install -r requirements.txt`

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Look at the console output for error messages
3. Make sure all prerequisites are installed correctly
4. Verify your `.env` file matches the example exactly

## 🎯 What's New

- ✅ **Graceful API fallbacks**: App works without any API keys
- ✅ **Robust error handling**: No more crashes from missing services
- ✅ **Deployment-ready**: Production configuration included
- ✅ **PostgreSQL support**: Better database performance
- ✅ **Improved normalizers**: Consistent output formats

