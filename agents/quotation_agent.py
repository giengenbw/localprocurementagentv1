from __future__ import annotations
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from core.quotation_extraction import ExtractedQuotation, extract_quotation_text

class Quote(BaseModel):
    supplier:str
    material_number:str
    quantity:Decimal=Field(gt=0)
    unit_price:Decimal=Field(ge=0)
    currency:str
    moq:Decimal|None=None
    delivery_days:int|None=None
    incoterms:str|None=None
    payment_terms:str|None=None
    validity_date:date|None=None

def compare_quotes(quotes:list[Quote], target_quantity:Decimal|None=None)->list[dict]:
    if not quotes:return []
    currencies={q.currency.upper() for q in quotes}
    if len(currencies)>1: raise ValueError("Currency conversion required; no exchange rate was supplied")
    eligible=[]
    for q in quotes:
        qty=target_quantity or q.quantity
        eligible.append((q,qty, q.moq is None or qty>=q.moq))
    comparable=[q.unit_price for q,_,ok in eligible if ok]
    low=min(comparable) if comparable else None
    result=[]
    for q,qty,ok in sorted(eligible,key=lambda x:(not x[2],x[0].unit_price)):
        deviation=((q.unit_price-low)/low*100) if ok and low not in (None,Decimal(0)) else None
        result.append({**q.model_dump(),"evaluated_quantity":qty,"total":qty*q.unit_price,"moq_eligible":ok,"deviation_from_low_pct":deviation})
    return result

class QuotationAgent:
    def extract(self,text:str)->ExtractedQuotation: return extract_quotation_text(text)
    def compare(self,quotes:list[Quote],target_quantity:Decimal|None=None): return compare_quotes(quotes,target_quantity)
