"""
Mock plagiarism service for testing without ML dependencies.
"""
import random

def check(text):
    """
    Mock function to check for plagiarism.
    In a real implementation, this would use scikit-learn for TF-IDF similarity.
    """
    if not text or len(text.strip()) < 50:
        return 0.0
    
    # Generate a realistic plagiarism score (usually low for legitimate papers)
    # Most academic papers should have low similarity scores
    plagiarism_score = random.uniform(5.0, 25.0)  # 5-25% similarity is typical
    
    return round(plagiarism_score, 1)