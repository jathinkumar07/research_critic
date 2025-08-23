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

def _clean_query(s: str, max_len: int = 110) -> str:
    s = " ".join(s.split())
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)  # control chars
    s = s.replace('“', '"').replace('”', '"').replace('’', "'")
    s = re.sub(r'\s+', ' ', s)
    # strip citation brackets and long numbers
    s = re.sub(r'\[[^\]]+\]', '', s)
    s = re.sub(r'\([^)]+\)', '', s)
    # limit length
    if len(s) > max_len:
        s = s[:max_len].rsplit(' ', 1)[0]
    return s.strip(" .,:;")

def extract_claims(text: str) -> List[str]:
    """Pick 3–8 short, factual-looking sentences, skipping headers and boilerplate."""
    if not text:
        return []
    sents = sent_tokenize(text)
    claims: List[str] = []
    for s in sents:
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
    return claims[:8]

def _init_service():
    """Return Google Fact Check discovery client if possible; else None."""
    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
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

def _call_rest(query: str) -> Dict[str, Any]:
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

def _status_from_reviews(fact_checks: List[Dict[str, Any]]) -> str:
    """
    Map claimReview ratings into coarse buckets.
    """
    if not fact_checks:
        return "no_verdict"

    truthy = 0
    falsy = 0

    for fc in fact_checks:
        reviews = fc.get("claimReview", []) if isinstance(fc, dict) else []
        if not isinstance(reviews, list):
            continue
        for r in reviews:
            rr = {}
            if isinstance(r, dict):
                rr = r.get("reviewRating", {}) or {}
            alt = (rr.get("alternateName") or rr.get("ratingValue") or "") if isinstance(rr, dict) else ""
            alt = str(alt).lower()
            if any(k in alt for k in ["true", "correct", "accurate", "mostly true"]):
                truthy += 1
            if any(k in alt for k in ["false", "incorrect", "inaccurate", "mostly false"]):
                falsy += 1

    if truthy > falsy and truthy > 0:
        return "verified"
    if falsy > truthy and falsy > 0:
        return "contradicted"
    return "no_verdict"

def fact_check_claims(claims: List[str]) -> List[Dict[str, Any]]:
    """
    Returns list of dicts:
      { "claim": str, "status": "verified|contradicted|no_verdict|api_error",
        "fact_checks": [raw items], "error": Optional[str] }
    """
    results: List[Dict[str, Any]] = []
    if not claims:
        return results

    service = _init_service()
    use_service = service is not None
    use_rest = (not use_service) and bool(API_KEY)

    if not use_service and not use_rest:
        # produce safe, non-empty placeholders to avoid “empty” UI
        for c in claims[:5]:
            results.append({
                "claim": c,
                "status": "no_verdict",
                "fact_checks": [],
                "error": "Fact-check not configured (no service account or API key)"
            })
        return results

    for i, c in enumerate(claims[:5]):
        if i:
            time.sleep(DELAY_BETWEEN_CALLS)
        try:
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
            # No emojis in logs -> avoid Windows cp1252 encoding error
            logger.warning("FactCheck API error: %s", e)
            results.append({
                "claim": c,
                "status": "api_error",
                "fact_checks": [],
                "error": str(e)
            })

    return results
