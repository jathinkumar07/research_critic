import re
import logging
from typing import Dict, List
from collections import Counter

logger = logging.getLogger(__name__)

def _sentences(text: str) -> List[str]:
    # simple sentence split; avoids NLTK dependency here
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if len(p.strip()) > 0]

def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9']+", s.lower())

def check_plagiarism(text: str) -> Dict:
    """
    Heuristic, offline plagiarism score:
      - measures internal repetition via 7-gram shingles
      - discounts very short/boilerplate lines
    Returns: {"plagiarism_score": float(0..1), "matching_sources": []}
    """
    if not text or len(text) < 200:
        return {"plagiarism_score": 0.0, "matching_sources": []}

    sents = [s for s in _sentences(text) if len(s) > 25]
    if len(sents) < 5:
        return {"plagiarism_score": 0.0, "matching_sources": []}

    all_shingles: Counter = Counter()
    for s in sents:
        toks = _tokenize(s)
        sh = _ngrams(toks, 7)
        all_shingles.update(sh)

    if not all_shingles:
        score = 0.0
    else:
        dup = sum(c for c in all_shingles.values() if c > 1)
        total = sum(all_shingles.values())
        score = min(1.0, dup / max(1, total))

    logger.info("Heuristic plagiarism score: %.3f", score)
    return {"plagiarism_score": float(score), "matching_sources": []}

# Backwards-compat function some routes call
def check(text: str) -> int:
    """Return percent [0..100] for legacy callers."""
    res = check_plagiarism(text)
    return int(round(100 * float(res.get("plagiarism_score", 0.0))))
