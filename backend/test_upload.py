#!/usr/bin/env python3
import requests
import os

def test_analyze_endpoint():
    """Test the analyze endpoint with the practical1.pdf file"""
    
    # Check if the PDF file exists
    pdf_path = "practical1.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Test PDF file not found: {pdf_path}")
        return False
    
    print(f"✅ Found test PDF: {pdf_path}")
    
    # Test health endpoint first
    try:
        health_response = requests.get("http://localhost:5000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend health check passed")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test analyze endpoint
    try:
        print("🔄 Testing analyze endpoint...")
        
        with open(pdf_path, 'rb') as file:
            files = {'file': (pdf_path, file, 'application/pdf')}
            response = requests.post(
                "http://localhost:5000/analyze", 
                files=files, 
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print(f"📊 Summary: {result.get('summary', 'N/A')[:100]}...")
            print(f"📈 Plagiarism Score: {result.get('plagiarism', 'N/A')}%")
            print(f"📚 Citations Found: {result.get('stats', {}).get('citations_count', 'N/A')}")
            print(f"📝 Word Count: {result.get('stats', {}).get('word_count', 'N/A')}")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis request failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Research Paper Analysis API")
    success = test_analyze_endpoint()
    if success:
        print("\n🎉 All tests passed! The backend is working correctly.")
    else:
        print("\n💥 Tests failed. Check the backend configuration.")