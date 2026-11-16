from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
_LOCK=Lock()

def _canonical(record:dict)->bytes:
    return json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")
def _last_hash(path:Path)->str:
    if not path.exists() or path.stat().st_size==0:return "0"*64
    last=path.read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(last)["record_hash"]
def audit(event:str,actor:str="system",details:dict|None=None,path:str|None=None)->dict:
    target=Path(path or os.getenv("AUDIT_LOG_PATH","./data/audit.jsonl")); target.parent.mkdir(parents=True,exist_ok=True)
    with _LOCK:
        record={"timestamp":datetime.now(timezone.utc).isoformat(),"event":event,"actor":actor,"details":details or {},"previous_hash":_last_hash(target)}
        record["record_hash"]=hashlib.sha256(_canonical(record)).hexdigest()
        with target.open("a",encoding="utf-8") as f:f.write(json.dumps(record,ensure_ascii=False,default=str)+"\n")
    return record

def verify_audit_chain(path:str)->tuple[bool,int,str|None]:
    target=Path(path)
    if not target.exists():return True,0,None
    previous="0"*64
    for index,line in enumerate(target.read_text(encoding="utf-8").splitlines(),1):
        try: record=json.loads(line)
        except json.JSONDecodeError:return False,index,"invalid JSON"
        claimed=record.pop("record_hash",None)
        if record.get("previous_hash")!=previous:return False,index,"previous hash mismatch"
        calculated=hashlib.sha256(_canonical(record)).hexdigest()
        if claimed!=calculated:return False,index,"record hash mismatch"
        previous=claimed
    return True,index if 'index' in locals() else 0,None
