import fitz  # PyMuPDF
import os

def extract_text_and_meta(pdf_path):
    """
    Extract text, word count, and title from PDF using PyMuPDF.
    Returns: (text, word_count, title)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"

    text = text.strip()
    word_count = len(text.split())
    title = doc.metadata.get("title") or os.path.basename(pdf_path)

    return text, word_count, title
