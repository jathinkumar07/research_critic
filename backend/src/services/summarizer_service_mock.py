"""
Mock summarizer service for testing without ML dependencies.
"""

def summarize(text):
    """
    Mock function to summarize text.
    In a real implementation, this would use HuggingFace transformers.
    """
    if not text or len(text.strip()) < 50:
        return "Text too short for summarization."
    
    # Extract first few sentences as a mock summary
    sentences = text.replace('\n', ' ').split('. ')
    
    # Create a mock summary
    summary = """
    This research paper presents comprehensive findings on the studied topic. 
    The methodology involved controlled experiments with statistical analysis 
    showing significant improvements in performance metrics. The results 
    demonstrate effectiveness with p < 0.05 significance level. The study 
    included proper citation of relevant academic sources and follows 
    established research protocols. The findings contribute to the existing 
    body of knowledge and suggest areas for future research.
    """
    
    return summary.strip()