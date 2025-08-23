import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

_DOI_RE = re.compile(r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b', re.IGNORECASE)
_URL_RE = re.compile(r'https?://[^\s<>")]+', re.IGNORECASE)

# APA-like in-text (Author, 2017) or (Author & Author, 2019)
_APA_INTEXT_RE = re.compile(r'\(([A-Z][A-Za-z\-]+(?:\s*&\s*[A-Z][A-Za-z\-]+)?(?:,\s*[A-Z][A-Za-z\-]+)*)\s*,\s*(\d{4}[a-z]?)\)', re.UNICODE)
# Numeric in-text [12] or [1,2,3]
_NUM_INTEXT_RE = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]')

_SECTION_HEAD_RE = re.compile(r'^\s*(references|bibliography|works\s+cited)\s*$', re.IGNORECASE)

def _split_lines(text: str) -> List[str]:
    return [ln.strip() for ln in text.splitlines()]

def _find_references_block(lines: List[str]) -> List[str]:
    """Return lines that appear to belong to the references section."""
    refs_start = None
    for idx, ln in enumerate(lines):
        if _SECTION_HEAD_RE.match(ln):
            refs_start = idx + 1
            break
    if refs_start is None:
        return []

    # collect until next big ALLCAPS/numbered header or end
    block = []
    for ln in lines[refs_start:]:
        if ln.strip() == "":
            block.append(ln)
            continue
        # crude next-section detector
        if re.match(r'^[A-Z][A-Z0-9 ._-]{3,}$', ln) and len(ln.split()) <= 6:
            # Ex: APPENDIX A, RESULTS, SUPPLEMENT, etc.
            break
        block.append(ln)
    return block

def _chunk_references(ref_lines: List[str]) -> List[str]:
    """Group reference entries from lines (empty line or line starting with [n] splits)."""
    entries, buf = [], []
    for ln in ref_lines:
        if not ln or re.match(r'^\s*\[\d+\]\s+', ln):  # IEEE style numbered
            if buf:
                entries.append(" ".join(buf).strip())
                buf = []
            if ln and re.match(r'^\s*\[\d+\]\s+', ln):
                buf.append(ln)
        else:
            buf.append(ln)
    if buf:
        entries.append(" ".join(buf).strip())
    # filter short junk
    return [e for e in entries if len(e) > 20]

def _extract_title_guess(ref: str) -> str:
    """Very rough title guess: remove DOI/URL and try to grab quoted or between year and period."""
    cleaned = _DOI_RE.sub('', ref)
    cleaned = _URL_RE.sub('', cleaned)
    m = re.search(r'"([^"]+)"|"([^"]+)"', cleaned)
    if m:
        return (m.group(1) or m.group(2)).strip()

    # try: after year ... before next period
    y = re.search(r'\((\d{4}[a-z]?)\)\.?\s*(.+?)\.', cleaned)
    if y:
        return y.group(2).strip()
    # fallback: first longish segment
    parts = [p.strip() for p in re.split(r'\.\s+', cleaned) if len(p.strip()) > 5]
    return parts[1] if len(parts) > 1 else (parts[0] if parts else cleaned[:120])

def validate(text: str) -> List[Dict]:
    """
    Parse in-text citations, DOIs/URLs, and the References section.
    Always returns a list of dicts: {raw, cleaned_title, doi, url, valid}
    Gracefully handles missing API keys by returning mock results.
    """
    if not text or not text.strip():
        return []

    try:
        lines = _split_lines(text)
        refs_block = _find_references_block(lines)
        ref_entries = _chunk_references(refs_block) if refs_block else []

        results: List[Dict] = []

        # 1) Bibliography entries
        for ref in ref_entries:
            doi = None
            url = None
            mdoi = _DOI_RE.search(ref)
            if mdoi:
                doi = mdoi.group(0)
            murl = _URL_RE.search(ref)
            if murl:
                url = murl.group(0)
            title = _extract_title_guess(ref)
            results.append({
                "raw": ref,
                "cleaned_title": title,
                "doi": doi,
                "url": url,
                "valid": bool(doi or url)  # simple validity rule
            })

        # 2) In-text APA-style (Author, 2017)
        for m in _APA_INTEXT_RE.finditer(text):
            raw = m.group(0)
            results.append({
                "raw": raw,
                "cleaned_title": "",
                "doi": None,
                "url": None,
                "valid": False
            })

        # 3) In-text numeric [1], [2,3]
        for m in _NUM_INTEXT_RE.finditer(text):
            raw = m.group(0)
            results.append({
                "raw": raw,
                "cleaned_title": "",
                "doi": None,
                "url": None,
                "valid": False
            })

        # If no citations found, return mock results to avoid empty UI
        if not results:
            results = [
                {
                    "raw": "Mock Citation (API not configured)",
                    "cleaned_title": "Citation validation not available",
                    "doi": None,
                    "url": None,
                    "valid": False
                }
            ]

        logger.info("Citations parsed: %d", len(results))
        return results

    except Exception as e:
        logger.warning(f"Citation validation failed: {e}")
        # Return mock result on error
        return [
            {
                "raw": "Citation validation error",
                "cleaned_title": "Unable to validate citations",
                "doi": None,
                "url": None,
                "valid": False
            }
        ]
