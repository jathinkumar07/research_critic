@echo off
REM AI Research Critic - Automated Setup Script for Windows
REM This script automates the setup process for Windows users

echo 🚀 AI Research Critic - Automated Setup
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.10+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH. Please install Node.js 16+ first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Step 1: Backend Setup
echo 📦 Setting up Backend...
cd backend

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating backend .env file...
    copy .env.example .env
    echo ⚠️  Please edit backend\.env and update the SECRET_KEY and JWT_SECRET_KEY
)

REM Initialize database
echo Initializing database...
flask db init 2>nul || echo Database already initialized
flask db migrate -m "Initial migration" 2>nul || echo Migration already exists
flask db upgrade

echo ✅ Backend setup complete
echo.

REM Step 2: Frontend Setup
echo 🎨 Setting up Frontend...
cd ..\frontend

REM Install dependencies
echo Installing Node.js dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating frontend .env file...
    copy .env.example .env
)

echo ✅ Frontend setup complete
echo.

REM Final instructions
echo 🎉 Setup Complete!
echo.
echo To start the application:
echo.
echo 1. Start Backend (in one command prompt):
echo    cd backend
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 2. Start Frontend (in another command prompt):
echo    cd frontend
echo    npm start
echo.
echo 3. Open browser to: http://localhost:3000
echo.
echo 💡 Tip: Keep both command prompt windows open while using the app
echo.
echo Happy analyzing! 📚🤖
pause