from pathlib import Path
import fitz
def extract_pdf_text(path:str,max_pages:int=50)->str:
    p=Path(path)
    if p.suffix.lower()!=".pdf": raise ValueError("Only PDF files are accepted")
    if p.stat().st_size>20*1024*1024: raise ValueError("PDF exceeds 20 MB")
    with fitz.open(path) as doc:
        if doc.page_count>max_pages: raise ValueError("PDF page limit exceeded")
        return "\n".join(page.get_text() for page in doc)
