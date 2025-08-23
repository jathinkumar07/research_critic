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
   cd ai-research-critic
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

### 2.4 Create Environment Configuration File

Create a file named `.env` in the `backend` directory with this content:

```bash
# Create .env file (Windows)
echo. > .env

# Create .env file (Mac/Linux)
touch .env
```

Open the `.env` file with any text editor (Notepad, VS Code, etc.) and add:

```env
# Basic Configuration (Required)
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too

# Database (SQLite - no setup needed)
SQLALCHEMY_DATABASE_URI=sqlite:///instance/app.db

# File Upload Settings
MAX_UPLOAD_MB=25
UPLOAD_DIR=uploads
REPORT_DIR=reports
CORPUS_DIR=corpus
ALLOWED_EXT=.pdf

# AI Features
USE_HF_SUMMARIZER=true
ALLOW_GUEST_UPLOADS=false

# API Keys (Optional - see API Keys section below)
# GOOGLE_API_KEY=your_google_api_key_here
# CROSSREF_API_KEY=your_crossref_api_key_here
# SEMANTIC_SCHOLAR_KEY=your_semantic_scholar_key_here
# FACTCHECK_USE=api_key
```

### 2.5 Initialize Database
```bash
# Initialize database migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations to create tables
flask db upgrade
```

### 2.6 Start Backend Server
```bash
python app.py
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

The application works without API keys using mock data, but for real results, set up these APIs:

### Google Fact Check API (for fact verification)

1. **Go to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Create a new project** or select existing one
3. **Enable the Fact Check Tools API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Fact Check Tools API"
   - Click "Enable"
4. **Create API Key**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the generated key
5. **Add to backend/.env**:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   FACTCHECK_USE=api_key
   ```

### Crossref API (for citation validation)

1. **Go to Crossref**: [www.crossref.org/documentation/retrieve-metadata/rest-api/](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
2. **Register for API access** (free)
3. **Get your API key**
4. **Add to backend/.env**:
   ```env
   CROSSREF_API_KEY=your_crossref_api_key_here
   ```

### Semantic Scholar API (for citation validation)

1. **Go to Semantic Scholar API**: [api.semanticscholar.org](https://api.semanticscholar.org)
2. **Register for API access**
3. **Get your API key**
4. **Add to backend/.env**:
   ```env
   SEMANTIC_SCHOLAR_KEY=your_semantic_scholar_key_here
   ```

**After adding API keys, restart the backend server** (Ctrl+C then `python app.py`)

## 🔧 Common Issues & Solutions

### ❌ "Python not found" or "pip not found"
- **Solution**: Python not installed or not in PATH
- **Fix**: Reinstall Python and check "Add to PATH" option

### ❌ "Node not found" or "npm not found"
- **Solution**: Node.js not installed properly
- **Fix**: Download and install Node.js from nodejs.org

### ❌ Backend won't start - "Module not found"
- **Solution**: Dependencies not installed or virtual environment not activated
- **Fix**: 
  ```bash
  cd backend
  source venv/bin/activate  # Mac/Linux
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  ```

### ❌ Frontend won't start - "Dependencies not installed"
- **Solution**: Node modules not installed
- **Fix**:
  ```bash
  cd frontend
  rm -rf node_modules package-lock.json
  npm install
  ```

### ❌ Database errors
- **Solution**: Database not initialized
- **Fix**:
  ```bash
  cd backend
  flask db init
  flask db migrate -m "Initial migration"
  flask db upgrade
  ```

### ❌ "CORS error" in browser
- **Solution**: Backend not running or wrong URL
- **Fix**: Ensure backend is running on `http://127.0.0.1:5000`

### ❌ File upload fails
- **Solution**: Check file size (max 25MB) and format (PDF only)
- **Fix**: Use smaller PDF files or check file format

## 📁 Project Structure

```
ai-research-critic/
├── 📂 backend/                 # Python Flask API
│   ├── 📂 src/
│   │   ├── 📂 models/          # Database models
│   │   ├── 📂 routes/          # API endpoints
│   │   ├── 📂 services/        # Business logic & AI services
│   │   └── 📂 utils/           # Utility functions
│   ├── 📂 uploads/             # Uploaded PDF files
│   ├── 📂 reports/             # Generated analysis reports
│   ├── 📂 corpus/              # Reference documents for plagiarism detection
│   ├── 📄 app.py               # Main Flask application
│   ├── 📄 config.py            # Configuration settings
│   ├── 📄 requirements.txt     # Python dependencies
│   └── 📄 .env                 # Environment variables (you create this)
├── 📂 frontend/                # React TypeScript UI
│   ├── 📂 src/
│   │   ├── 📂 components/      # Reusable UI components
│   │   ├── 📂 pages/          # Application pages
│   │   ├── 📂 contexts/       # React contexts
│   │   └── 📂 services/       # API communication
│   ├── 📂 public/             # Static assets
│   ├── 📄 package.json        # Node.js dependencies
│   └── 📄 .env                # Frontend environment variables (you create this)
└── 📄 README.md               # This file
```

## 🛠️ Tech Stack

### Backend Technologies
- **Python 3.10+** - Programming language
- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (development)
- **JWT** - Authentication
- **PyMuPDF** - PDF processing
- **HuggingFace Transformers** - AI text summarization
- **scikit-learn** - Machine learning for plagiarism detection
- **ReportLab** - PDF report generation

### Frontend Technologies
- **React 18** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Styling framework
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization

## 🎯 Usage Guide

### First Time Setup
1. **Register Account**: Click "Sign Up" and create your account
2. **Login**: Use your credentials to access the dashboard

### Analyzing Papers
1. **Go to Upload Page**: Click "Upload Document" in the navigation
2. **Select PDF File**: Choose a research paper (max 25MB)
3. **Wait for Processing**: Analysis takes 30-60 seconds
4. **View Results**: See summary, plagiarism score, citations, and critique
5. **Generate Report**: Download professional PDF reports
6. **Manage History**: View previous analyses in your dashboard

## 🔍 API Endpoints Reference

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh authentication token

### Document Management
- `POST /documents/upload` - Upload PDF file
- `GET /documents/:id` - Get specific document details
- `GET /documents` - List all user documents

### Analysis
- `POST /analysis/run` - Start analysis on uploaded document
- `GET /analysis/:id` - Get analysis results
- `GET /analysis` - List all user analyses

### Reports
- `POST /reports/:analysis_id/generate` - Generate PDF report
- `GET /reports/:report_id/download` - Download generated report
- `GET /reports` - List all user reports

## 🌐 Production Deployment

### Backend Deployment
1. **Set production environment**:
   ```env
   FLASK_ENV=production
   SECRET_KEY=strong-random-secret-key
   JWT_SECRET_KEY=strong-random-jwt-key
   ```

2. **Use PostgreSQL database**:
   ```env
   SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/dbname
   ```

3. **Deploy with Gunicorn**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

### Frontend Deployment
1. **Build for production**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Update API URL**:
   ```env
   REACT_APP_API_URL=https://your-backend-domain.com
   ```

3. **Serve with nginx/Apache** or deploy to Vercel/Netlify

## 🤝 Contributing

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** and test thoroughly
4. **Commit changes**: `git commit -m "Add feature description"`
5. **Push to branch**: `git push origin feature-name`
6. **Create Pull Request** on GitHub

## 📜 License

MIT License - see LICENSE file for details.

## 🧪 Testing Your Setup

After setup, verify everything works:

1. **Run the automated tests:**
   ```bash
   cd backend
   python simple_test.py
   ```

2. **Test the web interface:**
   - Open `http://localhost:3000`
   - Register a new account
   - Upload a sample PDF
   - Verify analysis completes

3. **For detailed testing instructions:** See `TESTING_GUIDE.md`
4. **For quick command reference:** See `QUICK_REFERENCE.md`

## 🆘 Need Help?

- **Check the troubleshooting section** above for common issues
- **Read TESTING_GUIDE.md** for comprehensive testing instructions
- **Ensure all prerequisites** are properly installed
- **Verify both servers are running** (backend on :5000, frontend on :3000)
- **Check console output** for error messages
- **Try the automated setup scripts** if manual setup fails

---

**🎉 Congratulations!** You now have a fully functional AI Research Critic application running locally. Upload a research paper and explore the powerful analysis features!

## 📚 Additional Resources

- **`QUICK_REFERENCE.md`** - Essential commands and troubleshooting
- **`TESTING_GUIDE.md`** - Comprehensive testing instructions  
- **`backend/.env.example`** - Backend configuration template
- **`frontend/.env.example`** - Frontend configuration template
- **`setup.sh`** - Automated setup for Mac/Linux
- **`setup.bat`** - Automated setup for Windows

## 🔄 Keeping Your Installation Updated

To update the application with new features:

```bash
# Pull latest changes
git pull origin main

# Update backend dependencies
cd backend
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
flask db upgrade

# Update frontend dependencies
cd ../frontend
npm install
```

