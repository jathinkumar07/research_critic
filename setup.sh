#!/bin/bash

# AI Research Critic - Automated Setup Script
# This script automates the setup process for Mac and Linux users

set -e  # Exit on any error

echo "🚀 AI Research Critic - Automated Setup"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10+ first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Step 1: Backend Setup
echo -e "${BLUE}📦 Setting up Backend...${NC}"
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating backend .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and update the SECRET_KEY and JWT_SECRET_KEY${NC}"
fi

# Initialize database
echo "Initializing database..."
flask db init || echo "Database already initialized"
flask db migrate -m "Initial migration" || echo "Migration already exists"
flask db upgrade

echo -e "${GREEN}✅ Backend setup complete${NC}"
echo ""

# Step 2: Frontend Setup
echo -e "${BLUE}🎨 Setting up Frontend...${NC}"
cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating frontend .env file..."
    cp .env.example .env
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"
echo ""

# Final instructions
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo -e "${BLUE}To start the application:${NC}"
echo ""
echo -e "${YELLOW}1. Start Backend (in one terminal):${NC}"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo -e "${YELLOW}2. Start Frontend (in another terminal):${NC}"
echo "   cd frontend"
echo "   npm start"
echo ""
echo -e "${YELLOW}3. Open browser to: http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}💡 Tip: Keep both terminal windows open while using the app${NC}"
echo ""
echo -e "${GREEN}Happy analyzing! 📚🤖${NC}"