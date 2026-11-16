from __future__ import annotations
import re
from datetime import datetime
from decimal import Decimal
from core.validation import PurchaseRequest, Language

DATE_PATTERNS=[r"(?P<d>\d{1,2})[.](?P<m>\d{1,2})[.](?P<y>\d{4})",r"(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})"]
def deterministic_extract(text:str)->PurchaseRequest:
    lower=text.lower(); language=Language.zh if re.search(r"[\u4e00-\u9fff]",text) else Language.en if any(x in lower for x in ["create","material","quantity","delivery"]) else Language.de
    material=None
    m=re.search(r"(?:material(?:nummer)?|material no\.?|物料(?:号|编号)?)\s*[:#]?\s*([A-Za-z0-9-]{3,30})",text,re.I)
    if m: material=m.group(1)
    qty=None; unit=None
    m=re.search(r"(\d+(?:[.,]\d+)?)\s*(stück|stk\.?|pcs?|pieces?|个|件)\b",text,re.I)
    if m: qty=Decimal(m.group(1).replace(",",".")); unit={"stück":"ST","stk":"ST","stk.":"ST","pc":"PC","pcs":"PC","piece":"PC","pieces":"PC","个":"ST","件":"ST"}.get(m.group(2).lower(),m.group(2).upper())
    delivery=None
    for p in DATE_PATTERNS:
        d=re.search(p,text)
        if d:
            try: delivery=datetime(int(d.group("y")),int(d.group("m")),int(d.group("d"))).date(); break
            except ValueError: pass
    return PurchaseRequest(material_number=material,quantity=qty,unit=unit,delivery_date=delivery,language=language)
