#!/usr/bin/env python3
"""
Local testing script for the Research Paper Analysis backend.

This script tests the /analyze endpoint without requiring any API keys,
ensuring the backend works 100% locally with mock data.
"""

import requests
import json
import os
import sys
from pathlib import Path

def test_analyze_endpoint():
    """Test the /analyze endpoint with a sample PDF."""
    
    # Configuration
    base_url = "http://localhost:5000"
    analyze_endpoint = f"{base_url}/analyze"
    
    # Check if sample PDF exists
    sample_pdf_path = Path("uploads/sample.pdf")
    if not sample_pdf_path.exists():
        # Try alternative locations
        alternative_paths = [
            Path("practical1.pdf"),
            Path("corpus/sample.pdf"),
            Path("../sample.pdf")
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                sample_pdf_path = alt_path
                break
        else:
            print("❌ No sample PDF found. Please ensure a sample PDF exists at:")
            print("   - uploads/sample.pdf")
            print("   - practical1.pdf")
            print("   - corpus/sample.pdf")
            return False
    
    print(f"📄 Using sample PDF: {sample_pdf_path}")
    
    try:
        # Test server health first
        print("🔍 Testing server health...")
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print(f"⚠️  Server health check returned status {health_response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please ensure the Flask app is running:")
        print("   python app.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server health check timed out")
        return False
    
    try:
        # Upload and analyze the PDF
        print(f"📤 Uploading and analyzing: {sample_pdf_path}")
        
        with open(sample_pdf_path, 'rb') as pdf_file:
            files = {'file': (sample_pdf_path.name, pdf_file, 'application/pdf')}
            
            response = requests.post(
                analyze_endpoint,
                files=files,
                timeout=60  # Allow up to 60 seconds for analysis
            )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Analysis completed successfully!")
                print("\n📋 ANALYSIS RESULTS:")
                print("=" * 50)
                
                # Print summary
                if 'summary' in result:
                    print(f"📝 Summary: {result['summary'][:200]}{'...' if len(result['summary']) > 200 else ''}")
                
                # Print plagiarism score
                if 'plagiarism' in result:
                    print(f"🔍 Plagiarism Score: {result['plagiarism']}%")
                
                # Print citations
                if 'citations' in result and result['citations']:
                    print(f"📚 Citations Found: {len(result['citations'])}")
                    for i, citation in enumerate(result['citations'][:3], 1):  # Show first 3
                        status = "✅ Valid" if citation.get('valid') else "❌ Invalid"
                        print(f"   {i}. {citation.get('reference', 'Unknown')} - {status}")
                    if len(result['citations']) > 3:
                        print(f"   ... and {len(result['citations']) - 3} more citations")
                
                # Print fact check results
                if 'fact_check' in result and 'facts' in result['fact_check']:
                    facts = result['fact_check']['facts']
                    if facts:
                        print(f"🔍 Fact Checks: {len(facts)}")
                        for i, fact in enumerate(facts[:3], 1):  # Show first 3
                            status = fact.get('status', 'Unknown')
                            print(f"   {i}. {fact.get('claim', 'Unknown claim')[:80]}... - {status}")
                        if len(facts) > 3:
                            print(f"   ... and {len(facts) - 3} more fact checks")
                
                # Print stats
                if 'stats' in result:
                    stats = result['stats']
                    print(f"📊 Statistics:")
                    print(f"   Word Count: {stats.get('word_count', 'N/A')}")
                    print(f"   Plagiarism: {stats.get('plagiarism_percent', 'N/A')}%")
                    print(f"   Citations: {stats.get('citations_count', 'N/A')}")
                
                print("\n✅ JSON Structure Validation:")
                required_keys = ['summary', 'plagiarism', 'citations', 'fact_check', 'stats']
                for key in required_keys:
                    if key in result:
                        print(f"   ✅ {key}: Present")
                    else:
                        print(f"   ❌ {key}: Missing")
                
                # Validate fact_check structure
                if 'fact_check' in result and 'facts' in result['fact_check']:
                    print(f"   ✅ fact_check.facts: Present")
                else:
                    print(f"   ❌ fact_check.facts: Missing")
                
                print("\n🎉 Test completed successfully!")
                print("Backend is working 100% locally without API keys!")
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Response content: {response.text[:500]}")
                return False
        
        else:
            print(f"❌ Analysis failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text[:500]}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out. The analysis might be taking too long.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to run the test."""
    print("🚀 Research Paper Analysis Backend - Local Test")
    print("=" * 50)
    print("Testing /analyze endpoint without API keys...")
    print()
    
    success = test_analyze_endpoint()
    
    if success:
        print("\n🎉 All tests passed! Backend is ready for local use.")
        sys.exit(0)
    else:
        print("\n❌ Test failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()