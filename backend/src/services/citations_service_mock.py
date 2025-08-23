"""
Mock citations service for testing without external API dependencies.
"""
import re
import random

def validate(text):
    """
    Mock function to validate citations.
    In a real implementation, this would use Semantic Scholar API.
    """
    if not text:
        return []
    
    # Simple regex to find citation-like patterns
    citation_patterns = [
        r'[A-Z][a-z]+ et al\. \(\d{4}\)',  # Smith et al. (2023)
        r'[A-Z][a-z]+ \(\d{4}\)',          # Jones (2022)
        r'[A-Z][a-z]+ and [A-Z][a-z]+ \(\d{4}\)',  # Brown and Wilson (2021)
        r'[A-Z][a-z]+, [A-Z]\. \(\d{4}\)', # Smith, J. (2023)
    ]
    
    citations = []
    
    for pattern in citation_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Extract a mock title from the citation
            if 'et al' in match:
                author = match.split(' et al')[0]
                cleaned_title = f"Research Study by {author} and Colleagues"
            elif ' and ' in match:
                authors = match.split(' (')[0]
                cleaned_title = f"Collaborative Study by {authors}"
            else:
                author = match.split(' (')[0]
                cleaned_title = f"Academic Paper by {author}"
            
            # Mock validation status
            status_options = ['verified', 'verified', 'verified', 'no_verdict', 'contradicted']
            status = random.choice(status_options)  # Bias toward verified
            
            citations.append({
                'raw': match,
                'cleaned_title': cleaned_title,
                'status': status
            })
    
    # Add some mock citations if none found
    if not citations:
        mock_citations = [
            {
                'raw': 'Smith et al. (2023)',
                'cleaned_title': 'Research Methodology in Modern Studies',
                'status': 'verified'
            },
            {
                'raw': 'Jones (2022)',
                'cleaned_title': 'Statistical Analysis Techniques',
                'status': 'verified'
            },
            {
                'raw': 'Brown and Wilson (2021)',
                'cleaned_title': 'Meta-Analysis of Research Findings',
                'status': 'no_verdict'
            }
        ]
        citations.extend(mock_citations)
    
    return citations[:10]  # Limit to 10 citations