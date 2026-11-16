from __future__ import annotations
import hashlib, math, re, sqlite3
from dataclasses import dataclass
from pathlib import Path
import httpx

@dataclass(frozen=True)
class DocumentChunk:
    document_id:str
    source_name:str
    chunk_index:int
    text:str
    sha256:str

@dataclass(frozen=True)
class SearchHit:
    document_id:str
    source_name:str
    chunk_index:int
    text:str
    score:float
    citation:str

class SafeTextChunker:
    def __init__(self,max_chars:int=1200,overlap:int=150):
        if max_chars<200 or overlap<0 or overlap>=max_chars: raise ValueError("Invalid chunk settings")
        self.max_chars=max_chars; self.overlap=overlap
    def chunk(self,text:str)->list[str]:
        normalized=re.sub(r"\r\n?","\n",text).strip()
        if not normalized:return []
        chunks=[]; start=0
        while start<len(normalized):
            end=min(start+self.max_chars,len(normalized))
            if end<len(normalized):
                boundary=max(normalized.rfind("\n",start,end),normalized.rfind(". ",start,end))
                if boundary>start+self.max_chars//2:end=boundary+1
            part=normalized[start:end].strip()
            if part:chunks.append(part)
            if end>=len(normalized):break
            start=max(end-self.overlap,start+1)
        return chunks

class KnowledgeStore:
    def __init__(self,path:str="data/knowledge.db"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._init()
    def connect(self):
        con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row; return con
    def _init(self):
        with self.connect() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS documents(document_id TEXT PRIMARY KEY,source_name TEXT NOT NULL,sha256 TEXT NOT NULL UNIQUE,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(document_id UNINDEXED,source_name UNINDEXED,chunk_index UNINDEXED,text,tokenize='unicode61');
            """)
    def ingest(self,source_name:str,text:str,chunker:SafeTextChunker|None=None)->dict:
        if len(text)>5_000_000:raise ValueError("Document text exceeds 5 MB safety limit")
        digest=hashlib.sha256(text.encode("utf-8")).hexdigest(); document_id=digest[:16]; chunker=chunker or SafeTextChunker(); parts=chunker.chunk(text)
        if not parts:raise ValueError("Document contains no extractable text")
        with self.connect() as con:
            existing=con.execute("select document_id from documents where sha256=?",(digest,)).fetchone()
            if existing:return {"document_id":existing[0],"chunks":0,"duplicate":True,"sha256":digest}
            con.execute("insert into documents(document_id,source_name,sha256) values(?,?,?)",(document_id,source_name,digest))
            con.executemany("insert into chunks(document_id,source_name,chunk_index,text) values(?,?,?,?)",[(document_id,source_name,i,p) for i,p in enumerate(parts)])
        return {"document_id":document_id,"chunks":len(parts),"duplicate":False,"sha256":digest}
    def search(self,query:str,limit:int=5)->list[SearchHit]:
        terms=re.findall(r"[\w.-]{2,}",query,flags=re.UNICODE)
        if not terms:return []
        expression=" OR ".join(f'"{t.replace(chr(34),"")}"' for t in terms[:12])
        with self.connect() as con:
            rows=con.execute("select document_id,source_name,chunk_index,text,bm25(chunks) rank from chunks where chunks match ? order by rank limit ?",(expression,max(1,min(limit,20)))).fetchall()
        return [SearchHit(r[0],r[1],int(r[2]),r[3],float(-r[4]),f"[{r[1]}#chunk-{r[2]}]") for r in rows]

class OllamaEmbeddingClient:
    def __init__(self,base_url="http://127.0.0.1:11434",model="nomic-embed-text",timeout=30):self.base_url=base_url.rstrip("/");self.model=model;self.timeout=timeout
    def embed(self,text:str)->list[float]:
        with httpx.Client(timeout=self.timeout) as client:r=client.post(f"{self.base_url}/api/embed",json={"model":self.model,"input":text})
        r.raise_for_status(); vectors=r.json().get("embeddings",[])
        if not vectors:raise RuntimeError("Ollama returned no embedding")
        return vectors[0]

def cosine_similarity(a:list[float],b:list[float])->float:
    if len(a)!=len(b) or not a:raise ValueError("Embedding dimensions do not match")
    denominator=math.sqrt(sum(x*x for x in a))*math.sqrt(sum(y*y for y in b))
    return sum(x*y for x,y in zip(a,b))/denominator if denominator else 0.0
