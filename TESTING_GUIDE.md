# 🧪 Testing Guide for AI Research Critic

This guide helps you verify that your AI Research Critic installation is working correctly.

## 🎯 Quick Test Checklist

Follow these tests in order to ensure everything is working:

### ✅ 1. Prerequisites Test

**Check Python Installation:**
```bash
python --version
# Should show: Python 3.10.x or higher
```

**Check Node.js Installation:**
```bash
node --version
# Should show: v16.x.x or higher

npm --version
# Should show: 8.x.x or higher
```

### ✅ 2. Backend Tests

**Navigate to backend directory:**
```bash
cd backend
```

**Activate virtual environment:**
```bash
# Mac/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

**Test 1: Check if Flask can start**
```bash
python app.py
```
**Expected output:**
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

**Test 2: Health Check (in new terminal)**
```bash
curl http://127.0.0.1:5000/health
```
**Expected output:**
```json
{
  "status": "success",
  "message": "AI Research Critic API is running",
  "data": {
    "service": "ai_research_critic",
    "health": "healthy"
  }
}
```

**Test 3: Database Connection**
```bash
# Stop the server (Ctrl+C) and run:
python -c "from src.extensions import db; from app import create_app; app = create_app(); app.app_context().push(); print('Database connection: OK')"
```

**Test 4: Run Backend Test Suite**
```bash
python simple_test.py
```
**Expected:** All services should return mock data successfully.

### ✅ 3. Frontend Tests

**Navigate to frontend directory:**
```bash
cd ../frontend
```

**Test 1: Check if React can start**
```bash
npm start
```
**Expected:** Browser opens to `http://localhost:3000` showing the app.

**Test 2: API Connection Test**
- Open browser to `http://localhost:3000`
- Open browser developer tools (F12)
- Look at Console tab - should see no red errors
- Look at Network tab when navigating - API calls should succeed

### ✅ 4. Full Integration Test

**With both servers running:**

1. **Registration Test:**
   - Go to `http://localhost:3000`
   - Click "Sign Up"
   - Create account with email and password
   - Should redirect to dashboard

2. **Login Test:**
   - Logout and login again
   - Should successfully authenticate

3. **File Upload Test:**
   - Go to "Upload Document"
   - Select a PDF file (any PDF, max 25MB)
   - Upload should succeed
   - Should show progress indicator

4. **Analysis Test:**
   - After upload, analysis should start automatically
   - Wait for completion (30-60 seconds)
   - Should show results with:
     - Summary text
     - Plagiarism percentage
     - Citation list
     - Fact check results

5. **Report Generation Test:**
   - Click "Generate Report" button
   - Should download a PDF report

## 🔧 Troubleshooting Failed Tests

### Backend Issues

**❌ "Module not found" errors:**
```bash
cd backend
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**❌ Database errors:**
```bash
cd backend
rm -rf migrations/  # Remove if exists
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**❌ Port 5000 already in use:**
```bash
# Find and kill process using port 5000
# Mac/Linux:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
# Note the PID and run: taskkill /PID <PID> /F
```

### Frontend Issues

**❌ "Dependencies not installed":**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**❌ Port 3000 already in use:**
- React will automatically try port 3001, 3002, etc.
- Or kill the process using port 3000

**❌ "CORS errors" in browser:**
- Ensure backend is running on `http://127.0.0.1:5000`
- Check that frontend `.env` has correct `REACT_APP_API_URL`

### API Integration Issues

**❌ "Network Error" when uploading:**
- Check both servers are running
- Verify URLs in browser developer tools
- Check file size (max 25MB)

**❌ Analysis stuck or fails:**
- Check backend console for error messages
- Verify PDF file is not corrupted
- Try with a different PDF file

## 🧪 Advanced Testing

### Load Testing
```bash
# Test multiple uploads (backend directory)
python test_endpoints.py
```

### API Testing with Curl
```bash
# Test upload endpoint directly
cd backend
./test_curl.sh
```

### Manual API Testing
```bash
# Test health endpoint
curl http://127.0.0.1:5000/health

# Test root endpoint
curl http://127.0.0.1:5000/

# Test file upload (with actual PDF)
curl -X POST -F "file=@path/to/your/file.pdf" http://127.0.0.1:5000/analyze
```

## 📊 Performance Expectations

### Normal Performance:
- **PDF Upload**: < 5 seconds for files under 10MB
- **Text Extraction**: 5-15 seconds depending on PDF size
- **AI Analysis**: 30-60 seconds total
- **Report Generation**: 10-20 seconds

### If Performance is Slow:
- Check available RAM (AI models need 2GB+ free)
- Ensure SSD storage for better I/O
- Close unnecessary applications
- Try smaller PDF files first

## 🎉 Success Indicators

**✅ Everything is working if:**
- Both servers start without errors
- Health check returns success
- You can register/login
- File upload works
- Analysis completes with results
- Reports can be generated and downloaded

**🎊 Congratulations!** Your AI Research Critic installation is fully functional!

## 🆘 Still Having Issues?

1. **Check all prerequisites** are installed correctly
2. **Verify environment files** are created and configured
3. **Check console outputs** for specific error messages
4. **Try the automated setup scripts** if you did manual setup
5. **Restart both servers** after making configuration changes
6. **Check file permissions** on uploaded files and directories

If problems persist, check the main README.md troubleshooting section for additional solutions.