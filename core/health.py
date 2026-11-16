from __future__ import annotations
import os,sqlite3
import httpx

def system_health(database_url:str|None=None,ollama_url:str|None=None)->dict:
    checks={}
    db_url=database_url or os.getenv("DATABASE_URL","sqlite:///./data/procurement.db")
    if db_url.startswith("sqlite:///"):
        path=db_url.removeprefix("sqlite:///")
        try:
            con=sqlite3.connect(path); checks["database"]={"status":"ok","integrity":con.execute("PRAGMA integrity_check").fetchone()[0]}; con.close()
        except Exception as exc: checks["database"]={"status":"error","error":type(exc).__name__}
    else: checks["database"]={"status":"unknown","detail":"Only SQLite health is implemented"}
    base=(ollama_url or os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434")).rstrip("/")
    try:
        r=httpx.get(f"{base}/api/tags",timeout=2); r.raise_for_status(); checks["ollama"]={"status":"ok","models":len(r.json().get("models",[]))}
    except Exception:checks["ollama"]={"status":"unavailable","optional":True}
    checks["sap"]={"status":"not_checked","detail":"Requires Windows SAP GUI session"}
    checks["graph"]={"status":"configured" if os.getenv("GRAPH_CLIENT_ID") else "not_configured"}
    overall="ok" if checks["database"]["status"]=="ok" else "degraded"
    return {"status":overall,"checks":checks}
