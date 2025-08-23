"""
Mock fact-check service for testing without external API dependencies.
"""
import re
import random

def extract_claims(text):
    """
    Mock function to extract factual claims from text.
    In a real implementation, this would use NLP to identify factual statements.
    """
    if not text:
        return []
    
    # Simple patterns to identify potential factual claims
    claim_indicators = [
        r'[0-9]+% of [^.]*\.',  # "95% of participants..."
        r'[Tt]he study shows [^.]*\.',  # "The study shows..."
        r'[Rr]esults demonstrate [^.]*\.',  # "Results demonstrate..."
        r'[Rr]esearch conducted at [^.]*\.',  # "Research conducted at..."
        r'[Ss]ignificant [^.]*with p < [0-9.]+',  # Statistical significance
        r'[Pp]erformance [^.]*improved by [0-9]+%',  # Performance claims
    ]
    
    claims = []
    sentences = text.split('.')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue
            
        for pattern in claim_indicators:
            if re.search(pattern, sentence, re.IGNORECASE):
                claims.append(sentence + '.')
                break
    
    # Add some mock claims if none found
    if not claims:
        mock_claims = [
            "95% of participants improved their performance.",
            "The study shows significant improvements in measured parameters.",
            "Research was conducted at Stanford University.",
            "Results demonstrate statistical significance with p < 0.05."
        ]
        claims.extend(mock_claims)
    
    return claims[:8]  # Limit to 8 claims

def fact_check_claims(claims):
    """
    Mock function to fact-check extracted claims.
    In a real implementation, this would use Google Fact Check API.
    """
    if not claims:
        return []
    
    fact_checked_claims = []
    
    for claim in claims:
        # Mock fact-checking result
        status_options = ['verified', 'verified', 'no_verdict', 'no_verdict', 'contradicted']
        status = random.choice(status_options)  # Bias toward verified/no_verdict
        
        result = {
            'claim': claim,
            'status': status,
            'fact_checks': [],
            'error': None
        }
        
        # Add mock fact check details for verified/contradicted claims
        if status == 'verified':
            result['fact_checks'] = [
                {
                    'title': 'Academic Research Verification',
                    'publisher': 'Research Database',
                    'url': 'https://example.com/research-verification',
                    'rating': 'True'
                }
            ]
        elif status == 'contradicted':
            result['fact_checks'] = [
                {
                    'title': 'Counter-Evidence Found',
                    'publisher': 'Fact Check Organization',
                    'url': 'https://example.com/fact-check',
                    'rating': 'False'
                }
            ]
        
        fact_checked_claims.append(result)
    
    return fact_checked_claims