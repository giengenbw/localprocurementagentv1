from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

def backup_sqlite(source:str,destination_dir:str,keep:int=14)->dict:
    src=Path(source); dest=Path(destination_dir)
    if not src.exists():raise FileNotFoundError(src)
    dest.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target=dest/f"procurement-{stamp}.db"
    with sqlite3.connect(src) as source_conn, sqlite3.connect(target) as target_conn: source_conn.backup(target_conn)
    integrity=sqlite3.connect(target).execute("PRAGMA integrity_check").fetchone()[0]
    if integrity!="ok": target.unlink(missing_ok=True); raise RuntimeError(f"Backup integrity check failed: {integrity}")
    backups=sorted(dest.glob("procurement-*.db"),reverse=True)
    for old in backups[max(keep,1):]: old.unlink()
    result={"backup":str(target),"size":target.stat().st_size,"integrity":integrity,"created_at":datetime.now(timezone.utc).isoformat()}
    (dest/"latest.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
