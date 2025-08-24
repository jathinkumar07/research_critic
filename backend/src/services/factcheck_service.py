import os
import time
import re
import logging
from typing import List, Dict, Any

import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt is available (safe no-op if already present)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

logger = logging.getLogger(__name__)

# ---- Env wiring (accept multiple names to avoid confusion) ----
SERVICE_ACCOUNT_FILE = (
    os.getenv("FACTCHECK_SERVICE_ACCOUNT") or
    os.getenv("GOOGLE_FACTCHECK_SERVICE_ACCOUNT_FILE") or
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)
API_KEY = (
    os.getenv("GOOGLE_FACT_CHECK_API_KEY") or
    os.getenv("GOOGLE_API_KEY") or
    os.getenv("FACTCHECK_API_KEY")
)

FACTCHECK_TIMEOUT = float(os.getenv("FACTCHECK_TIMEOUT", "8.0"))
MAX_RETRIES = int(os.getenv("FACTCHECK_MAX_RETRIES", "2"))
DELAY_BETWEEN_CALLS = float(os.getenv("FACTCHECK_DELAY", "0.35"))

def _is_valid_service_account_file(filepath: str) -> bool:
    """Check if the service account file exists and is valid."""
    if not filepath or not os.path.exists(filepath):
        return False
    try:
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Check for required keys in service account JSON
            required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            return all(key in data for key in required_keys)
    except Exception as e:
        logger.warning(f"Invalid service account file {filepath}: {e}")
        return False

def _has_valid_credentials() -> bool:
    """Check if we have valid credentials for fact-checking."""
    # Check service account file
    if SERVICE_ACCOUNT_FILE and _is_valid_service_account_file(SERVICE_ACCOUNT_FILE):
        return True
    
    # Check API key (should not be placeholder)
    if API_KEY and API_KEY != "your-api-key-here" and len(API_KEY) > 10:
        return True
    
    return False

def _clean_query(s: str, max_len: int = 110) -> str:
    s = " ".join(s.split())
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)  # control chars
    s = s.replace('"', '"').replace('"', '"').replace("'", "'")
    s = re.sub(r'\s+', ' ', s)
    # strip citation brackets and long numbers
    s = re.sub(r'\[[^\]]+\]', '', s)
    s = re.sub(r'\([^)]+\)', '', s)
    # limit length
    if len(s) > max_len:
        s = s[:max_len].rsplit(' ', 1)[0]
    return s.strip(" .,:;")

def extract_claims(text: str) -> List[str]:
    """
    Pick 3–8 short, factual-looking sentences, skipping headers and boilerplate.
    This function is safe and will never fail.
    """
    try:
        if not text:
            return []
        
        sents = sent_tokenize(text)
        claims: List[str] = []
        
        for s in sents:
            try:
                st = s.strip()
                low = st.lower()
                if any(h in low for h in ["abstract", "keywords", "references", "appendix", "figure", "table"]):
                    continue
                if len(st) < 40 or len(st) > 220:
                    continue
                if st.endswith(':') or st.endswith(';'):
                    continue
                # avoid sentences dominated by citations/parentheses
                if st.count('(') + st.count(')') >= 2 or st.count('[') >= 1:
                    continue
                # avoid % of digits noise
                if len(re.findall(r'\d', st)) > len(st) * 0.25:
                    continue
                claims.append(st)
                if len(claims) >= 8:
                    break
            except Exception as e:
                logger.warning(f"Error processing sentence for claims: {e}")
                continue
        
        return claims[:8]
    except Exception as e:
        logger.error(f"Error extracting claims: {e}")
        return []

def _init_service():
    """Return Google Fact Check discovery client if possible; else None."""
    if not SERVICE_ACCOUNT_FILE or not _is_valid_service_account_file(SERVICE_ACCOUNT_FILE):
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        return build("factchecktools", "v1alpha1", credentials=creds, cache_discovery=False)
    except Exception as e:
        logger.warning("Could not init FactCheck service account client: %s", e)
        return None

def _call_service(service, query: str) -> Dict[str, Any]:
    """Call the service with proper error handling."""
    try:
        q = _clean_query(query)
        if not q:
            return {}
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                req = service.claims().search(query=q)
                return req.execute()
            except Exception as e:
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(0.4 * attempt)
    except Exception as e:
        logger.warning(f"Service call failed: {e}")
        return {}

def _call_rest(query: str) -> Dict[str, Any]:
    """Call the REST API with proper error handling."""
    try:
        q = _clean_query(query)
        if not q or not API_KEY:
            return {}
        
        import requests
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {"query": q, "key": API_KEY}
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = requests.get(url, params=params, timeout=FACTCHECK_TIMEOUT)
                data = {}
                try:
                    data = r.json()
                except Exception:
                    data = {}
                r.raise_for_status()
                return data
            except Exception as e:
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(0.4 * attempt)
    except Exception as e:
        logger.warning(f"REST API call failed: {e}")
        return {}

def _status_from_reviews(fact_checks: List[Dict[str, Any]]) -> str:
    """
    Map claimReview ratings into coarse buckets.
    """
    try:
        if not fact_checks:
            return "no_verdict"

        truthy = 0
        falsy = 0

        for fc in fact_checks:
            try:
                reviews = fc.get("claimReview", []) if isinstance(fc, dict) else []
                if not isinstance(reviews, list):
                    continue
                for r in reviews:
                    try:
                        rr = {}
                        if isinstance(r, dict):
                            rr = r.get("reviewRating", {}) or {}
                        alt = (rr.get("alternateName") or rr.get("ratingValue") or "") if isinstance(rr, dict) else ""
                        alt = str(alt).lower()
                        if any(k in alt for k in ["true", "correct", "accurate", "mostly true"]):
                            truthy += 1
                        if any(k in alt for k in ["false", "incorrect", "inaccurate", "mostly false"]):
                            falsy += 1
                    except Exception as e:
                        logger.warning(f"Error processing review: {e}")
                        continue
            except Exception as e:
                logger.warning(f"Error processing fact check: {e}")
                continue

        if truthy > falsy and truthy > 0:
            return "verified"
        if falsy > truthy and falsy > 0:
            return "contradicted"
        return "no_verdict"
    except Exception as e:
        logger.error(f"Error determining status from reviews: {e}")
        return "no_verdict"

def fact_check_claims(claims: List[str]) -> List[Dict[str, Any]]:
    """
    Returns list of dicts:
      { "claim": str, "status": "verified|contradicted|no_verdict|api_error",
        "fact_checks": [raw items], "error": Optional[str] }
    
    This function is designed to never crash and always return properly formatted results.
    """
    results: List[Dict[str, Any]] = []
    
    try:
        if not claims:
            return results

        # Check if we have valid credentials
        has_valid_creds = _has_valid_credentials()
        
        if not has_valid_creds:
            logger.info("No valid fact-check credentials found, returning placeholder results")
            # Return safe placeholder results
            for c in claims[:5]:
                results.append({
                    "claim": c,
                    "status": "no_verdict",
                    "fact_checks": [],
                    "error": "Fact-check API not configured (no valid credentials)"
                })
            return results

        # Try to initialize service
        service = _init_service()
        use_service = service is not None
        use_rest = (not use_service) and bool(API_KEY)

        if not use_service and not use_rest:
            # Fallback to placeholder results
            for c in claims[:5]:
                results.append({
                    "claim": c,
                    "status": "no_verdict",
                    "fact_checks": [],
                    "error": "Fact-check service unavailable"
                })
            return results

        # Process claims
        for i, c in enumerate(claims[:5]):
            try:
                if i:
                    time.sleep(DELAY_BETWEEN_CALLS)
                
                data = _call_service(service, c) if use_service else _call_rest(c)
                fcs = data.get("claims", []) if isinstance(data, dict) else []
                status = _status_from_reviews(fcs)
                
                results.append({
                    "claim": c,
                    "status": status,
                    "fact_checks": fcs,
                    "error": None
                })
            except Exception as e:
                logger.warning("FactCheck processing error for claim: %s", e)
                results.append({
                    "claim": c,
                    "status": "api_error",
                    "fact_checks": [],
                    "error": str(e)
                })

        return results
        
    except Exception as e:
        logger.error(f"Critical error in fact_check_claims: {e}")
        # Return safe fallback even in case of critical errors
        fallback_results = []
        for c in (claims or [])[:5]:
            fallback_results.append({
                "claim": c if isinstance(c, str) else "Processing error",
                "status": "api_error",
                "fact_checks": [],
                "error": f"Service error: {str(e)}"
            })
        return fallback_results if fallback_results else [
            {
                "claim": "Service unavailable",
                "status": "api_error", 
                "fact_checks": [],
                "error": "Critical service error"
            }
        ]
