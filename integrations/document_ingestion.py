from __future__ import annotations
from pathlib import Path
from integrations.pdf_reader import extract_pdf_text
from integrations.attachment_security import assess_attachment
ALLOWED_TEXT={".txt",".csv"}
def extract_local_document(path:str)->tuple[str,str]:
    p=Path(path)
    if not p.exists() or not p.is_file():raise FileNotFoundError(p)
    content=p.read_bytes(); assessment=assess_attachment(p.name,content)
    if not assessment.safe_for_extraction:raise ValueError(assessment.reason)
    suffix=p.suffix.lower()
    if suffix==".pdf":text=extract_pdf_text(path)
    elif suffix in ALLOWED_TEXT:text=content.decode("utf-8-sig",errors="strict")
    else:raise ValueError("This Phase 7 extractor supports PDF, TXT and CSV only")
    return p.name,text
