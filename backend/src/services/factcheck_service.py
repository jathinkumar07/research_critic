import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def extract_claims(text: str) -> List[str]:
    """Extract factual claims from text."""
    if not text:
        return []
    
    # Simple sentence extraction
    sentences = text.split('.')
    claims = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 40 and len(sentence) < 220:
            if not any(h in sentence.lower() for h in ["abstract", "keywords", "references", "appendix"]):
                claims.append(sentence)
                if len(claims) >= 5:
                    break
    
    return claims[:5]

def fact_check_claims(claims: List[str]) -> List[Dict[str, Any]]:
    """
    Returns list of dicts:
      { "claim": str, "status": "verified|contradicted|no_verdict|api_error",
        "fact_checks": [raw items], "error": Optional[str] }
    Gracefully handles missing API keys by returning mock results.
    """
    results: List[Dict[str, Any]] = []
    if not claims:
        return results

    # Check if Google Fact Check is configured
    service_account_file = (
        os.getenv("FACTCHECK_SERVICE_ACCOUNT") or
        os.getenv("GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE") or
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    
    api_key = (
        os.getenv("GOOGLE_FACT_CHECK_API_KEY") or
        os.getenv("GOOGLE_API_KEY") or
        os.getenv("FACTCHECK_API_KEY")
    )

    # If no API keys configured, return mock results
    if not service_account_file and not api_key:
        for c in claims[:5]:
            results.append({
                "claim": c,
                "status": "no_verdict",
                "fact_checks": [],
                "error": "Fact-check not configured (no service account or API key)"
            })
        return results

    # If API keys are configured, try to use them
    for c in claims[:5]:
        try:
            # This would normally call the Google Fact Check API
            # For now, return mock results
            results.append({
                "claim": c,
                "status": "no_verdict",
                "fact_checks": [],
                "error": "Fact-check API not fully implemented"
            })
        except Exception as e:
            logger.warning("FactCheck API error: %s", e)
            results.append({
                "claim": c,
                "status": "api_error",
                "fact_checks": [],
                "error": str(e)
            })

    return results