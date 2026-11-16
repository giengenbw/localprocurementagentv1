from contextlib import asynccontextmanager
from decimal import Decimal
from fastapi import FastAPI
from pydantic import BaseModel, Field
from agents.procurement_agent import ProcurementAgent
from agents.quotation_agent import QuotationAgent, Quote
from core.quotation_extraction import ExtractedQuotation
from database.db import init_db
from core.health import system_health
from core.knowledge import KnowledgeStore
from agents.knowledge_agent import KnowledgeAgent
from core.config_validation import validate_runtime_config
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
app=FastAPI(title="Local Procurement AI Agent",version="0.2.0",lifespan=lifespan)
agent=ProcurementAgent(); quotation_agent=QuotationAgent()
knowledge_agent=KnowledgeAgent(KnowledgeStore())

class ChatRequest(BaseModel):
    message:str=Field(min_length=1,max_length=10000)
    use_llm:bool=True
class QuotationTextRequest(BaseModel):
    text:str=Field(min_length=1,max_length=200000)
class KnowledgeQuery(BaseModel):
    question:str=Field(min_length=2,max_length=2000)
    limit:int=Field(default=5,ge=1,le=20)
class CompareRequest(BaseModel):
    quotations:list[Quote]
    target_quantity:Decimal|None=None
@app.get("/health")
def health(): return {"status":"ok","local_only":True,"phase":7}
@app.get("/api/system/health")
def detailed_health(): return system_health()
@app.post("/api/chat")
def chat(req:ChatRequest): return agent.handle(req.message,req.use_llm).model_dump(mode="json")
@app.post("/api/quotations/extract",response_model=ExtractedQuotation)
def extract_quote(req:QuotationTextRequest): return quotation_agent.extract(req.text)
@app.post("/api/knowledge/search")
def knowledge_search(req:KnowledgeQuery): return knowledge_agent.grounded_context(req.question,req.limit)
@app.get("/api/system/config-validation")
def config_validation(): return [x.__dict__ for x in validate_runtime_config()]
@app.post("/api/quotations/compare")
def compare(req:CompareRequest): return quotation_agent.compare(req.quotations,req.target_quantity)
