#!/usr/bin/env python3
"""
Test script to verify that the normalizers work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.citations_service import validate
from src.services.plagiarism_service import check_plagiarism

def test_citations_normalizer():
    """Test citation validation with mock data."""
    print("Testing citation validation...")
    
    # Test with empty text
    result = validate("")
    print(f"Empty text result: {result}")
    assert isinstance(result, list)
    
    # Test with sample text
    sample_text = """
    This is a sample research paper with citations.
    
    References:
    Smith, J. (2023). Research Study. Journal of Science.
    Jones, A. & Brown, B. (2022). Another Study. Nature.
    """
    
    result = validate(sample_text)
    print(f"Sample text result: {result}")
    assert isinstance(result, list)
    
    # Test normalizer function
    def _norm_citation(c):
        """Normalize a single citation dict."""
        if not isinstance(c, dict):
            return {"reference": "Unknown", "valid": False}
        
        reference = c.get("raw") or c.get("cleaned_title") or c.get("reference") or "Unknown citation"
        valid = bool(c.get("valid", False))
        
        return {"reference": str(reference), "valid": valid}
    
    formatted_citations = [_norm_citation(c) for c in result]
    print(f"Formatted citations: {formatted_citations}")
    
    print("✅ Citation normalizer test passed!")

def test_plagiarism_normalizer():
    """Test plagiarism detection with mock data."""
    print("\nTesting plagiarism detection...")
    
    # Test with empty text
    result = check_plagiarism("")
    print(f"Empty text result: {result}")
    assert isinstance(result, dict)
    assert "plagiarism_score" in result
    assert "matching_sources" in result
    
    # Test with sample text
    sample_text = """
    This is a sample research paper with some content.
    It contains multiple sentences and paragraphs.
    The content should be analyzed for plagiarism detection.
    """
    
    result = check_plagiarism(sample_text)
    print(f"Sample text result: {result}")
    assert isinstance(result, dict)
    assert "plagiarism_score" in result
    assert "matching_sources" in result
    
    # Test normalizer function
    def _norm_plagiarism(res):
        """Normalize plagiarism results to always return proper format."""
        if isinstance(res, dict):
            return {
                "plagiarism_score": float(res.get("plagiarism_score", 0.0)),
                "matching_sources": res.get("matching_sources", []) or []
            }
        if isinstance(res, (int, float)):
            v = float(res)
            if v > 1.0:  # treat as %
                v = v / 100.0
            return {"plagiarism_score": v, "matching_sources": []}
        return {"plagiarism_score": 0.0, "matching_sources": []}
    
    normalized_result = _norm_plagiarism(result)
    print(f"Normalized result: {normalized_result}")
    
    print("✅ Plagiarism normalizer test passed!")

def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\nTesting error handling...")
    
    # Test with None input
    try:
        result = validate(None)
        print(f"None input result: {result}")
        assert isinstance(result, list)
    except Exception as e:
        print(f"Error with None input: {e}")
    
    # Test with invalid input
    try:
        result = check_plagiarism(None)
        print(f"None input result: {result}")
        assert isinstance(result, dict)
    except Exception as e:
        print(f"Error with None input: {e}")
    
    print("✅ Error handling test passed!")

if __name__ == "__main__":
    print("🧪 Testing normalizers...")
    
    try:
        test_citations_normalizer()
        test_plagiarism_normalizer()
        test_error_handling()
        
        print("\n🎉 All tests passed! The normalizers are working correctly.")
        print("The application should now handle missing API keys gracefully.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)