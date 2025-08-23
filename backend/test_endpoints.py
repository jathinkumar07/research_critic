#!/usr/bin/env python3
"""
Test script to demonstrate the fact-check and citation endpoints
without needing API keys (using mock data).
"""

import json

# Sample test data
SAMPLE_TEXT = """
Climate change is a pressing global issue. The Earth's temperature has increased by 1.1 degrees Celsius since the late 19th century. 
According to NASA, 2021 was one of the hottest years on record. The Arctic ice is melting at an unprecedented rate.
Carbon dioxide levels in the atmosphere have reached 415 parts per million, the highest in human history.

References:
1. Hansen, J., et al. (2010). Global surface temperature change. Reviews of Geophysics, 48(4), RG4004.
2. IPCC (2021). Climate Change 2021: The Physical Science Basis. Cambridge University Press.
3. Steffen, W., et al. (2018). Trajectories of the Earth System in the Anthropocene. PNAS, 115(33), 8252-8259.
"""

SAMPLE_CITATIONS = [
    "Hansen, J., et al. (2010). Global surface temperature change. Reviews of Geophysics, 48(4), RG4004.",
    "IPCC (2021). Climate Change 2021: The Physical Science Basis. Cambridge University Press.",
    "Smith, A. B. (2020). Non-existent paper about climate. Fake Journal, 1(1), 1-10."
]

def test_factcheck_endpoint():
    """Test the fact-check endpoint with sample text."""
    print("🧪 Testing Fact-Check Endpoint")
    print("=" * 50)
    
    # Simulate API request payload
    request_payload = {
        "text": SAMPLE_TEXT
    }
    
    print(f"Request payload: {json.dumps(request_payload, indent=2)}")
    print("\nExpected response format:")
    print("""
{
  "status": "success",
  "message": "Fact-checked N claims successfully",
  "data": {
    "claims": [
      {
        "claim": "original sentence",
        "status": "verified|contradicted|no_verdict",
        "fact_checks": [...],
        "error": null
      }
    ],
    "source": "google_factcheck",
    "total_claims": N
  }
}
""")

def test_citations_endpoint():
    """Test the citations endpoint with sample citations."""
    print("\n🧪 Testing Citations Endpoint")
    print("=" * 50)
    
    # Test with direct citations list
    request_payload = {
        "citations": SAMPLE_CITATIONS
    }
    
    print(f"Request payload: {json.dumps(request_payload, indent=2)}")
    print("\nExpected response format:")
    print("""
{
  "status": "success",
  "message": "Validated N citations successfully",
  "data": {
    "citations": [
      {
        "citation": "original citation text",
        "valid": true|false,
        "doi": "10.xxxx/xxxxx" or null,
        "status": "Valid|Not Found|Invalid Format",
        "cleaned_title": "extracted title"
      }
    ],
    "total_citations": N,
    "valid_count": N,
    "invalid_count": N,
    "source": "crossref|semantic_scholar|mock"
  }
}
""")

def test_health_endpoints():
    """Test health check endpoints."""
    print("\n🧪 Testing Health Endpoints")
    print("=" * 50)
    
    print("GET /health - Main API health check")
    print("GET /api/factcheck/health - Fact-check service health")
    print("GET /api/citations/health - Citations service health")
    
    print("\nExpected response format:")
    print("""
{
  "status": "success",
  "message": "Service is running",
  "data": {
    "service": "service_name",
    "health": "healthy"
  }
}
""")

def main():
    """Main test demonstration."""
    print("🚀 Research Paper Analysis API - Endpoint Testing")
    print("=" * 60)
    print("This script demonstrates the expected behavior of the")
    print("fact-check and citation endpoints with mock data.")
    print("=" * 60)
    
    test_factcheck_endpoint()
    test_citations_endpoint()
    test_health_endpoints()
    
    print("\n📝 Testing Instructions:")
    print("=" * 50)
    print("1. Start the Flask server: python app.py")
    print("2. Test fact-check endpoint:")
    print("   POST http://localhost:5000/api/factcheck/run")
    print("   Content-Type: application/json")
    print('   Body: {"text": "Your text here"}')
    print()
    print("3. Test citations endpoint:")
    print("   POST http://localhost:5000/api/citations/validate")
    print("   Content-Type: application/json")
    print('   Body: {"citations": ["Citation 1", "Citation 2"]}')
    print()
    print("4. Check health endpoints:")
    print("   GET http://localhost:5000/health")
    print("   GET http://localhost:5000/api/factcheck/health")
    print("   GET http://localhost:5000/api/citations/health")
    print()
    print("💡 Note: Without API keys in .env, the system will use")
    print("   realistic mock data for testing purposes.")

if __name__ == "__main__":
    main()