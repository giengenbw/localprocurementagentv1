from core.llm import OllamaClient
from core.parser import deterministic_extract
from core.workflow import build_plan
class ProcurementAgent:
    def __init__(self,llm=None): self.llm=llm or OllamaClient()
    def handle(self,text:str,use_llm:bool=True):
        if len(text)>10000: raise ValueError("Input too long")
        try: req=self.llm.extract_purchase_request(text) if use_llm else deterministic_extract(text)
        except Exception: req=deterministic_extract(text)
        return build_plan(req)
