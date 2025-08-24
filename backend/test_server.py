#!/usr/bin/env python3
"""
Test script for the AI Research Critic API
Demonstrates server functionality with actual PDF analysis
"""
import requests
import json
import os
import time

def test_api():
    """Test the API endpoints with actual PDF files."""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI Research Critic API")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    print()
    
    # Test root endpoint
    print("2. Testing root endpoint...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   API Version: {response.json()['data']['version']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    print()
    
    # Test PDF analysis with sample file
    print("3. Testing PDF analysis...")
    pdf_files = ["uploads/EJ1172284.pdf", "uploads/sample.pdf"]
    
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            print(f"⚠️ PDF file not found: {pdf_file}")
            continue
            
        print(f"   Testing with: {pdf_file}")
        
        try:
            with open(pdf_file, 'rb') as f:
                files = {'file': (os.path.basename(pdf_file), f, 'application/pdf')}
                response = requests.post(f"{base_url}/analyze", files=files, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ PDF analysis successful")
                print(f"   Document: {data['data']['document_info']['title'][:50]}...")
                print(f"   Word count: {data['data']['document_info']['word_count']}")
                print(f"   Plagiarism score: {data['data']['plagiarism_score']}%")
                print(f"   Citations found: {len(data['data']['citations'])}")
                print(f"   Summary: {data['data']['summary'][:100]}...")
                
                # Save result for inspection
                result_file = f"test_result_{os.path.basename(pdf_file).replace('.pdf', '.json')}"
                with open(result_file, 'w') as rf:
                    json.dump(data, rf, indent=2)
                print(f"   Full result saved to: {result_file}")
                
            else:
                print(f"❌ PDF analysis failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ PDF analysis failed: {e}")
        
        print()
    
    print("🎉 API testing completed!")
    return True

if __name__ == "__main__":
    print("Starting API test suite...")
    print("Make sure the server is running on http://localhost:5000")
    print()
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            pass
        time.sleep(2)
        print(f"   Waiting... ({i+1}/10)")
    else:
        print("❌ Server not responding. Please start the server first.")
        print("   Run: python3 app_improved.py")
        exit(1)
    
    print()
    test_api()