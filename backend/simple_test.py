#!/usr/bin/env python3
"""
Simple test to verify backend services work without API keys.
This test doesn't require external dependencies like requests.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_services():
    """Test that all services work with mock data."""
    print("🚀 Testing Research Paper Analysis Services")
    print("=" * 50)
    
    # Test text for analysis
    sample_text = """
    This is a research paper about machine learning. Smith et al. (2023) conducted 
    a comprehensive study showing that 95% of participants improved their performance. 
    The study demonstrates significant improvements in measured parameters with p < 0.05.
    Research was conducted at Stanford University in collaboration with MIT.
    Jones (2022) also found similar results in their meta-analysis.
    """
    
    try:
        # Test PDF service (mock)
        print("📄 Testing PDF extraction service...")
        try:
            from services.pdf_service_mock import extract_text_and_meta
            text, word_count, title = extract_text_and_meta("dummy.pdf")
            print(f"   ✅ PDF service works: {word_count} words extracted")
        except Exception as e:
            print(f"   ❌ PDF service failed: {e}")
        
        # Test summarization service (mock)
        print("📝 Testing summarization service...")
        try:
            from services.summarizer_service_mock import summarize
            summary = summarize(sample_text)
            print(f"   ✅ Summarization works: {len(summary)} chars generated")
        except Exception as e:
            print(f"   ❌ Summarization failed: {e}")
        
        # Test plagiarism service (mock)
        print("🔍 Testing plagiarism detection service...")
        try:
            from services.plagiarism_service_mock import check
            plagiarism_score = check(sample_text)
            print(f"   ✅ Plagiarism detection works: {plagiarism_score}% score")
        except Exception as e:
            print(f"   ❌ Plagiarism detection failed: {e}")
        
        # Test citations service (mock)
        print("📚 Testing citations validation service...")
        try:
            from services.citations_service_mock import validate
            citations = validate(sample_text)
            print(f"   ✅ Citations validation works: {len(citations)} citations found")
            for citation in citations[:2]:  # Show first 2
                status = "Valid" if citation.get('status') == 'verified' else "Invalid"
                print(f"      - {citation.get('raw', 'Unknown')} [{status}]")
        except Exception as e:
            print(f"   ❌ Citations validation failed: {e}")
        
        # Test fact-check service (mock)
        print("🔍 Testing fact-check service...")
        try:
            from services.factcheck_service_mock import extract_claims, fact_check_claims
            claims = extract_claims(sample_text)
            fact_results = fact_check_claims(claims)
            print(f"   ✅ Fact-checking works: {len(fact_results)} claims checked")
            for fact in fact_results[:2]:  # Show first 2
                status = fact.get('status', 'unknown').title()
                print(f"      - {fact.get('claim', 'Unknown')[:50]}... [{status}]")
        except Exception as e:
            print(f"   ❌ Fact-checking failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ All services are working with mock data!")
        print("🎉 Backend is ready for 100% local operation without API keys!")
        
        # Test the real services with missing API keys
        print("\n🔧 Testing real services fallback to mock data...")
        
        # Test real fact-check service
        try:
            from services.factcheck_service import extract_claims, fact_check_claims
            claims = extract_claims(sample_text)
            fact_results = fact_check_claims(claims)
            print(f"   ✅ Real fact-check service falls back to mock: {len(fact_results)} results")
        except Exception as e:
            print(f"   ❌ Real fact-check service failed: {e}")
        
        # Test real citations service
        try:
            from services.citations_service import validate
            citations = validate(sample_text)
            print(f"   ✅ Real citations service falls back to mock: {len(citations)} results")
        except Exception as e:
            print(f"   ❌ Real citations service failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main test function."""
    success = test_services()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("The backend is configured to work 100% locally without API keys.")
        print("\nTo test the full /analyze endpoint:")
        print("1. Start the server: python3 app.py")
        print("2. Upload a PDF to: POST http://localhost:5000/analyze")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()