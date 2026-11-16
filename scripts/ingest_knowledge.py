from __future__ import annotations
import argparse,json
from core.knowledge import KnowledgeStore
from integrations.document_ingestion import extract_local_document
def main():
    p=argparse.ArgumentParser(description="Ingest an approved local document into the procurement knowledge base")
    p.add_argument("path");p.add_argument("--database",default="data/knowledge.db");args=p.parse_args()
    name,text=extract_local_document(args.path);result=KnowledgeStore(args.database).ingest(name,text);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
