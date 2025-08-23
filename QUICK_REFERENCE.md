# 🚀 Quick Reference Card

## 📋 Essential Commands

### 🔄 Starting the Application

**Backend (Terminal 1):**
```bash
cd backend
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
python app.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm start
```

**URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://127.0.0.1:5000`

### 🛠️ Setup Commands

**Initial Setup (Mac/Linux):**
```bash
./setup.sh
```

**Initial Setup (Windows):**
```cmd
setup.bat
```

**Manual Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Manual Frontend Setup:**
```bash
cd frontend
npm install
cp .env.example .env
```

### 🧪 Testing Commands

**Backend Health Check:**
```bash
curl http://127.0.0.1:5000/health
```

**Run Backend Tests:**
```bash
cd backend
python simple_test.py
```

**Test File Upload:**
```bash
cd backend
./test_curl.sh
```

### 🔧 Troubleshooting Commands

**Reset Backend:**
```bash
cd backend
rm -rf venv migrations instance
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
pip install -r requirements.txt
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Reset Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Kill Processes on Ports:**
```bash
# Mac/Linux
lsof -ti:5000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### 📁 Important File Locations

**Configuration Files:**
- `backend/.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables
- `backend/config.py` - Backend configuration
- `frontend/src/services/api.ts` - API configuration

**Log Files:**
- Backend console output
- Browser developer tools (F12) → Console tab

**Upload Directory:**
- `backend/uploads/` - Uploaded PDF files
- `backend/reports/` - Generated reports

### 🔑 Environment Variables Quick Reference

**Backend (.env):**
```env
FLASK_ENV=development
SECRET_KEY=change-this-secret-key
JWT_SECRET_KEY=change-this-jwt-key
SQLALCHEMY_DATABASE_URI=sqlite:///instance/app.db
MAX_UPLOAD_MB=25
USE_HF_SUMMARIZER=true

# Optional API Keys
GOOGLE_API_KEY=your_google_api_key
CROSSREF_API_KEY=your_crossref_key
SEMANTIC_SCHOLAR_KEY=your_semantic_scholar_key
FACTCHECK_USE=api_key
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://127.0.0.1:5000
```

### 🎯 Common File Operations

**Upload Test File:**
- Use any PDF file under 25MB
- Research papers work best
- Sample files in `backend/uploads/` if available

**Check Logs:**
- Backend: Watch terminal where `python app.py` is running
- Frontend: Check browser Console (F12)

### 📞 API Endpoints

**Health Check:**
```bash
GET http://127.0.0.1:5000/health
```

**Upload & Analyze:**
```bash
POST http://127.0.0.1:5000/analyze
Content-Type: multipart/form-data
Body: file=<PDF_FILE>
```

**Authentication:**
```bash
POST http://127.0.0.1:5000/auth/register
POST http://127.0.0.1:5000/auth/login
```

---

**💡 Pro Tip:** Bookmark this page for quick access to commands during development!