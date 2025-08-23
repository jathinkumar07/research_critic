#!/bin/bash

# Simple curl test for the /analyze endpoint
echo "🚀 Testing /analyze endpoint with curl"
echo "======================================="

# Check if server is running
echo "🔍 Checking server health..."
curl -s http://localhost:5000/health | head -c 100
echo

# Test the analyze endpoint with sample PDF
echo "📤 Testing /analyze endpoint..."
curl -X POST \
  -F "file=@uploads/sample.pdf" \
  http://localhost:5000/analyze \
  | head -c 500

echo
echo "✅ Test completed!"