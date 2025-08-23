"""
Mock PDF service for testing without PyMuPDF dependency.
"""
import os

def extract_text_and_meta(file_path):
    """
    Mock function to extract text and metadata from PDF.
    In a real implementation, this would use PyMuPDF.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file size for word count estimation
    file_size = os.path.getsize(file_path)
    estimated_word_count = max(100, file_size // 10)  # Rough estimation
    
    filename = os.path.basename(file_path)
    title = filename.replace('.pdf', '').replace('_', ' ').title()
    
    # Mock extracted text
    mock_text = f"""
    Research Paper: {title}
    
    Abstract:
    This research paper presents findings on various aspects of the study. 
    The methodology involved controlled experiments with peer review processes.
    Results show significant improvements in the measured parameters.
    
    Introduction:
    Recent studies have shown that 95% of participants improved their performance 
    when following the proposed methodology. This finding is consistent with 
    previous research conducted at Stanford University and MIT.
    
    Methodology:
    The study was conducted over a period of 12 months with a sample size of 
    500 participants. Statistical analysis was performed using standard methods.
    
    Results:
    The results demonstrate significant statistical significance with p < 0.05.
    Performance metrics improved by an average of 23% across all test groups.
    
    Citations:
    Smith et al. (2023) demonstrated similar improvements in their study.
    Jones (2022) published findings in Nature journal that support these results.
    Brown and Wilson (2021) conducted a meta-analysis of related research.
    
    Conclusion:
    The findings suggest that the proposed approach is effective and can be 
    applied in various contexts. Future research should explore additional 
    applications of this methodology.
    """
    
    return mock_text.strip(), estimated_word_count, title