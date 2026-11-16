from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass(frozen=True)
class DeliveryAssessment:
    status:str
    days_vs_requested:int|None
    days_overdue:int
    requires_reminder:bool
    escalation_level:int
    reason:str

def assess_delivery(requested:date, confirmed:date|None, confirmation_received:bool, today:date|None=None, delivered:bool=False)->DeliveryAssessment:
    today=today or date.today()
    if delivered: return DeliveryAssessment("delivered",None,0,False,0,"Delivery recorded")
    if not confirmation_received or confirmed is None:
        overdue=max((today-requested).days,0)
        level=2 if overdue>=7 else 1 if overdue>0 else 0
        return DeliveryAssessment("missing_confirmation",None,overdue,True,level,"Supplier confirmation is missing")
    delta=(requested-confirmed).days  # positive=early, negative=late
    overdue=max((today-confirmed).days,0)
    if overdue>0:
        level=3 if overdue>=14 else 2 if overdue>=7 else 1
        return DeliveryAssessment("overdue",delta,overdue,True,level,"Confirmed delivery date has passed")
    if delta<0:
        return DeliveryAssessment("confirmed_late",delta,0,True,1,"Supplier-confirmed date is later than requested")
    return DeliveryAssessment("on_time",delta,0,False,0,"Confirmed date meets requested date")

def delivery_status(requested:date,confirmed:date|None,today:date|None=None)->str:
    return assess_delivery(requested,confirmed,confirmed is not None,today).status

class DeliveryAgent:
    def assess(self,*args,**kwargs): return assess_delivery(*args,**kwargs)
    def reminder_draft(self,supplier_email:str,po_number:str,assessment:DeliveryAssessment,language="de")->dict:
        if language=="de":
            subject=f"Lieferstatus Bestellung {po_number}"
            body=f"Guten Tag,\n\nbitte bestätigen Sie uns kurzfristig den aktuellen Lieferstatus zu unserer Bestellung {po_number}."
            if assessment.status=="overdue": body+=f" Der bestätigte Liefertermin ist seit {assessment.days_overdue} Tag(en) überschritten."
            body+="\n\nBitte nennen Sie uns einen verbindlichen Liefertermin.\n\nVielen Dank!"
        elif language=="zh":
            subject=f"订单 {po_number} 交货状态"
            body=f"您好，\n\n请尽快确认订单 {po_number} 的当前交货状态，并提供明确的交货日期。\n\n谢谢！"
        else:
            subject=f"Delivery status for purchase order {po_number}"
            body=f"Hello,\n\nplease confirm the current delivery status for purchase order {po_number} and provide a firm delivery date.\n\nThank you."
        return {"subject":subject,"body":{"contentType":"Text","content":body},"toRecipients":[{"emailAddress":{"address":supplier_email}}],"requires_approval":True,"escalation_level":assessment.escalation_level}
