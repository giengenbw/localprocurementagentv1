from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from agents.email_agent import EmailAgent
@dataclass(frozen=True)
class OpenPO:
    po_number:str; material_number:str|None; supplier_email:str|None; requested_delivery_date:date|None
@dataclass(frozen=True)
class ConfirmationMatch:
    po_number:str|None; status:str; reason:str; confirmed_delivery_date:date|None=None
class ConfirmationAgent:
    def __init__(self): self.email=EmailAgent()
    def match(self,subject:str,body:str,sender:str|None,open_pos:list[OpenPO])->ConfirmationMatch:
        facts=self.email.classify(subject,body,sender)
        if not facts["is_order_confirmation"]: return ConfirmationMatch(None,"not_confirmation","Email is not classified as an order confirmation")
        po=facts["purchase_order"]
        if not po: return ConfirmationMatch(None,"manual_review","No purchase order number was found")
        candidates=[x for x in open_pos if x.po_number==po]
        if len(candidates)!=1: return ConfirmationMatch(po,"manual_review","Purchase order match is missing or ambiguous")
        row=candidates[0]
        if row.supplier_email and facts["sender_email"] and row.supplier_email.lower()!=facts["sender_email"].lower(): return ConfirmationMatch(po,"manual_review","Sender does not match the recorded supplier contact")
        if row.material_number and facts["material_number"] and row.material_number.lower()!=facts["material_number"].lower(): return ConfirmationMatch(po,"manual_review","Material number does not match the open PO")
        return ConfirmationMatch(po,"matched","Order confirmation matched deterministically",facts["delivery_date"])
