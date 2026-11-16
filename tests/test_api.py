from fastapi.testclient import TestClient
from app.main import app
def test_chat_without_ollama():
 r=TestClient(app).post("/api/chat",json={"message":"Material 123456, 10 Stück, 15.12.2026","use_llm":False})
 assert r.status_code==200 and r.json()["request"]["material_number"]=="123456"

def test_quote_extract_endpoint():
 r=TestClient(app).post("/api/quotations/extract",json={"text":"Supplier: Demo\nMaterial No: M-1\nQuantity: 3\nUnit Price: 2,50\nCurrency: EUR"})
 assert r.status_code==200 and r.json()["unit_price"]=="2.50"

def test_quote_compare_endpoint_decimal_quantity():
 payload={"target_quantity":"100","quotations":[{"supplier":"A","material_number":"M","quantity":"100","unit_price":"10","currency":"EUR","moq":"1"}]}
 r=TestClient(app).post("/api/quotations/compare",json=payload)
 assert r.status_code==200 and r.json()[0]["total"]==1000

def test_phase6_health_endpoint(monkeypatch,tmp_path):
 db=tmp_path/"health.db"
 monkeypatch.setenv("DATABASE_URL",f"sqlite:///{db}")
 r=TestClient(app).get("/api/system/health")
 assert r.status_code==200 and r.json()["checks"]["database"]["integrity"]=="ok"

def test_phase7_knowledge_search_endpoint(tmp_path,monkeypatch):
 from app import main
 from agents.knowledge_agent import KnowledgeAgent
 from core.knowledge import KnowledgeStore
 store=KnowledgeStore(str(tmp_path/"knowledge.db")); store.ingest("policy.txt","Payment term is 30 days after chassis delivery.")
 monkeypatch.setattr(main,"knowledge_agent",KnowledgeAgent(store))
 r=TestClient(app).post("/api/knowledge/search",json={"question":"payment chassis","limit":3})
 assert r.status_code==200 and r.json()["context"][0]["citation"]=="[policy.txt#chunk-0]"

def test_phase7_config_validation_endpoint():
 r=TestClient(app).get("/api/system/config-validation")
 assert r.status_code==200
