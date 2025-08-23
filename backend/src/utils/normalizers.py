"""
Normalization utilities for service outputs.
Ensures consistent data structures and graceful fallbacks.
"""
import logging
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)

def normalize_plagiarism_result(result: Any) -> Dict[str, Any]:
    """
    Normalize plagiarism service output to consistent format.
    
    Expected output: {"plagiarism_score": float, "matching_sources": list}
    """
    try:
        if isinstance(result, dict):
            score = float(result.get("plagiarism_score", 0.0))
            sources = result.get("matching_sources", [])
            if not isinstance(sources, list):
                sources = []
            
            # Ensure score is between 0 and 1
            if score > 1.0:
                score = score / 100.0
            score = max(0.0, min(1.0, score))
            
            return {
                "plagiarism_score": score,
                "matching_sources": sources
            }
        
        elif isinstance(result, (int, float)):
            score = float(result)
            if score > 1.0:
                score = score / 100.0
            score = max(0.0, min(1.0, score))
            
            return {
                "plagiarism_score": score,
                "matching_sources": []
            }
        
        else:
            logger.warning(f"Unexpected plagiarism result type: {type(result)}")
            return {"plagiarism_score": 0.0, "matching_sources": []}
            
    except Exception as e:
        logger.error(f"Error normalizing plagiarism result: {e}")
        return {"plagiarism_score": 0.0, "matching_sources": []}

def normalize_citations_result(result: Any) -> List[Dict[str, Any]]:
    """
    Normalize citations service output to consistent format.
    
    Expected output: list[{"reference": str, "valid": bool}]
    """
    try:
        if not result:
            return []
        
        if isinstance(result, str):
            # Single string result - likely an error or fallback
            return [{"reference": "Unknown", "valid": False}]
        
        if isinstance(result, list):
            normalized = []
            for item in result:
                if isinstance(item, dict):
                    # Extract reference text from various possible fields
                    reference = (
                        item.get("raw") or
                        item.get("cleaned_title") or 
                        item.get("reference") or
                        "Unknown"
                    )
                    
                    # Determine validity
                    valid = bool(item.get("valid", False))
                    
                    normalized.append({
                        "reference": str(reference),
                        "valid": valid
                    })
                elif isinstance(item, str):
                    normalized.append({
                        "reference": item,
                        "valid": False
                    })
            
            return normalized
        
        else:
            logger.warning(f"Unexpected citations result type: {type(result)}")
            return [{"reference": "Unknown", "valid": False}]
            
    except Exception as e:
        logger.error(f"Error normalizing citations result: {e}")
        return [{"reference": "Unknown", "valid": False}]

def normalize_factcheck_result(result: Any) -> List[Dict[str, str]]:
    """
    Normalize fact-check service output to consistent format.
    
    Expected output: list[{"claim": str, "status": str}]
    """
    try:
        if not result:
            return []
        
        if isinstance(result, str):
            # Single string result - likely an error
            return [{"claim": "Unable to extract claims", "status": "Unverified"}]
        
        if isinstance(result, list):
            normalized = []
            for item in result:
                if isinstance(item, dict):
                    claim = str(item.get("claim", "Unknown claim"))
                    
                    # Normalize status
                    status = item.get("status", "no_verdict")
                    if status in ["verified", "true"]:
                        normalized_status = "Verified"
                    elif status in ["contradicted", "false"]:
                        normalized_status = "Contradicted"
                    elif status in ["api_error", "error"]:
                        normalized_status = "Unverified"
                    else:
                        normalized_status = "Unverified"
                    
                    normalized.append({
                        "claim": claim,
                        "status": normalized_status
                    })
                elif isinstance(item, str):
                    normalized.append({
                        "claim": item,
                        "status": "Unverified"
                    })
            
            return normalized
        
        else:
            logger.warning(f"Unexpected factcheck result type: {type(result)}")
            return [{"claim": "Unable to process", "status": "Unverified"}]
            
    except Exception as e:
        logger.error(f"Error normalizing factcheck result: {e}")
        return [{"claim": "Processing error", "status": "Unverified"}]

def safe_call_service(service_func, *args, **kwargs) -> Any:
    """
    Safely call a service function with error handling and fallback.
    """
    try:
        return service_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Service call failed: {service_func.__name__}: {e}")
        # Return appropriate fallback based on expected service type
        func_name = getattr(service_func, '__name__', str(service_func))
        
        if 'plagiarism' in func_name.lower():
            return {"plagiarism_score": 0.0, "matching_sources": []}
        elif 'citation' in func_name.lower():
            return [{"reference": "Unknown", "valid": False}]
        elif 'fact' in func_name.lower():
            return [{"claim": "Service unavailable", "status": "Unverified"}]
        else:
            return None