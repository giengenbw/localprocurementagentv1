from __future__ import annotations
import base64, hashlib, re
from dataclasses import dataclass

ALLOWED_EXTENSIONS={".pdf",".xlsx",".xls",".docx",".txt",".csv"}
BLOCKED_EXTENSIONS={".exe",".com",".bat",".cmd",".ps1",".vbs",".js",".msi",".scr",".dll",".lnk",".iso",".html",".htm"}
@dataclass(frozen=True)
class AttachmentAssessment:
    safe_for_extraction: bool
    reason: str
    sha256: str|None=None
    size: int=0

def assess_attachment(name:str, content:bytes, max_mb:int=20)->AttachmentAssessment:
    normalized=name.strip().lower()
    suffix="."+normalized.rsplit(".",1)[-1] if "." in normalized else ""
    if not name or re.search(r"[\\/]",name): return AttachmentAssessment(False,"invalid filename",size=len(content))
    if suffix in BLOCKED_EXTENSIONS: return AttachmentAssessment(False,"executable or active-content extension blocked",size=len(content))
    if suffix not in ALLOWED_EXTENSIONS: return AttachmentAssessment(False,"file type not allowlisted",size=len(content))
    if len(content)>max_mb*1024*1024: return AttachmentAssessment(False,"attachment exceeds size limit",size=len(content))
    if content.startswith(b"MZ"): return AttachmentAssessment(False,"executable file signature blocked",size=len(content))
    return AttachmentAssessment(True,"allowlisted for text extraction; antivirus scan still required",hashlib.sha256(content).hexdigest(),len(content))

def decode_graph_attachment(item:dict)->bytes:
    value=item.get("contentBytes")
    if not isinstance(value,str): raise ValueError("Graph attachment does not contain inline contentBytes")
    return base64.b64decode(value,validate=True)
