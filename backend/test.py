import fitz  # PyMuPDF real package



pdf_path = "sample.pdf"  # replace with an actual PDF in your backend folder

doc = fitz.open(pdf_path)
text = ""
for page in doc:
    text += page.get_text()

print("Extracted text:\n", text[:500])  # show only first 500 chars
