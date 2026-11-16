from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import date, datetime
from email.utils import parseaddr

PO_RE=re.compile(r"(?<!\d)(45\d{8})(?!\d)")
MATERIAL_RE=re.compile(r"(?:material(?:nummer|\s*(?:no\.?|number))?|物料(?:号|编号)?)\s*[:#]?\s*([A-Z0-9._/-]{3,40})",re.I)
DATE_RE=re.compile(r"(?<!\d)(\d{1,2})[.](\d{1,2})[.](\d{4})(?!\d)|(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)")
@dataclass(frozen=True)
class EmailFacts:
    category:str
    sender_email:str|None
    purchase_order:str|None
    material_number:str|None
    delivery_date:date|None
    is_order_confirmation:bool
    suspicious_instruction:bool

class EmailAgent:
    def classify(self,subject:str,body:str,sender:str|None=None)->dict:
        text=f"{subject}\n{body}"; lower=text.lower()
        po=PO_RE.search(text); mat=MATERIAL_RE.search(text); delivery=self._date(text)
        confirmation=bool(re.search(r"auftragsbestätigung|order confirmation|订单确认",text,re.I))
        if confirmation: category="order_confirmation"
        elif re.search(r"lieferverzug|delay|verspät|延期|延迟",text,re.I): category="delivery_delay"
        elif re.search(r"angebot|quotation|quote|报价",text,re.I): category="quotation"
        elif re.search(r"rechnung|invoice|发票",text,re.I): category="invoice"
        else: category="other"
        suspicious=bool(re.search(r"ignore (?:all |previous )?instructions|system prompt|execute (?:this )?command|powershell|cmd\.exe|忽略.*指令",lower,re.I))
        sender_email=parseaddr(sender or "")[1] or None
        return EmailFacts(category,sender_email,po.group(1) if po else None,mat.group(1) if mat else None,delivery,confirmation,suspicious).__dict__
    def _date(self,text:str)->date|None:
        for m in DATE_RE.finditer(text):
            try:
                if m.group(1): return date(int(m.group(3)),int(m.group(2)),int(m.group(1)))
                return date(int(m.group(4)),int(m.group(5)),int(m.group(6)))
            except ValueError: continue
        return None
    def draft_confirmation_request(self,to:str,po_number:str,language="de")->dict:
        if not PO_RE.fullmatch(po_number): raise ValueError("A valid 10-digit PO number beginning with 45 is required")
        if language=="de": subject=f"Auftragsbestätigung zur Bestellung {po_number}"; body=f"Guten Tag,\n\nbitte senden Sie uns die Auftragsbestätigung zu unserer Bestellung {po_number}.\n\nVielen Dank!"
        elif language=="zh": subject=f"请确认订单 {po_number}"; body=f"您好，\n\n请向我们发送订单 {po_number} 的订单确认。\n\n谢谢！"
        else: subject=f"Order confirmation for purchase order {po_number}"; body=f"Hello,\n\nplease send us the order confirmation for purchase order {po_number}.\n\nThank you."
        return {"subject":subject,"body":{"contentType":"Text","content":body},"toRecipients":[{"emailAddress":{"address":to}}]}
