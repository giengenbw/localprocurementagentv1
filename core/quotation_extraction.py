from __future__ import annotations
import hashlib, json, re
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ExtractedQuotation(BaseModel):
    model_config=ConfigDict(extra="forbid", str_strip_whitespace=True)
    supplier: str | None = None
    quote_reference: str | None = None
    material_number: str | None = None
    quantity: Decimal | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)
    currency: str | None = None
    moq: Decimal | None = Field(default=None, gt=0)
    delivery_days: int | None = Field(default=None, ge=0)
    incoterms: str | None = None
    payment_terms: str | None = None
    validity_date: str | None = None
    source_hash: str
    missing_fields: list[str] = Field(default_factory=list)
    @field_validator("currency")
    @classmethod
    def currency_upper(cls,v): return v.upper() if v else v

REQUIRED=("supplier","material_number","quantity","unit_price","currency")
def extract_quotation_text(text: str) -> ExtractedQuotation:
    if len(text)>200_000: raise ValueError("Quotation text exceeds safety limit")
    h=hashlib.sha256(text.encode("utf-8")).hexdigest()
    def one(pattern):
        m=re.search(pattern,text,re.I|re.M); return m.group(1).strip() if m else None
    supplier=one(r"(?:supplier|lieferant|供应商)\s*[:#]\s*([^\n\r]+)")
    ref=one(r"(?:quotation|angebot|报价)(?:\s*(?:no\.?|nr\.?|编号))?\s*[:#]\s*([A-Z0-9._/-]+)")
    material=one(r"(?:material(?:\s*(?:no\.?|number))?|materialnummer|物料号)\s*[:#]\s*([A-Z0-9._/-]+)")
    q=one(r"(?:quantity|menge|数量)\s*[:#]\s*([0-9.,]+)")
    price=one(r"(?:unit price|einzelpreis|stückpreis|单价)\s*[:#]\s*([0-9.,]+)")
    currency=one(r"(?:currency|währung|币种)\s*[:#]\s*([A-Z]{3})")
    moq=one(r"(?:MOQ|mindestbestellmenge)\s*[:#]\s*([0-9.,]+)")
    days=one(r"(?:delivery time|lieferzeit|交期)\s*[:#]\s*(\d+)\s*(?:days?|tage|天)")
    incoterms=one(r"(?:incoterms?|lieferbedingung)\s*[:#]\s*([A-Z]{3}(?:\s+[^\n\r]+)?)")
    payment=one(r"(?:payment terms?|zahlungsbedingungen?|付款条件)\s*[:#]\s*([^\n\r]+)")
    validity=one(r"(?:valid(?:ity)? until|gültig bis|有效期至)\s*[:#]\s*([0-9./-]+)")
    def dec(v):
        if not v:return None
        s=v.replace(" ","")
        if "," in s and "." in s: s=s.replace(".","").replace(",",".")
        else: s=s.replace(",",".")
        return Decimal(s)
    obj=ExtractedQuotation(supplier=supplier,quote_reference=ref,material_number=material,quantity=dec(q),unit_price=dec(price),currency=currency,moq=dec(moq),delivery_days=int(days) if days else None,incoterms=incoterms,payment_terms=payment,validity_date=validity,source_hash=h)
    obj.missing_fields=[x for x in REQUIRED if getattr(obj,x) is None]
    return obj
