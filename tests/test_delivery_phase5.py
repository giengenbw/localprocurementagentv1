from datetime import date
from agents.delivery_agent import DeliveryAgent,assess_delivery
def test_difference_rule_early_positive_late_negative():
 assert assess_delivery(date(2026,11,20),date(2026,11,18),True,date(2026,11,15)).days_vs_requested==2
 assert assess_delivery(date(2026,11,20),date(2026,11,25),True,date(2026,11,15)).days_vs_requested==-5
def test_missing_confirmation_and_overdue_escalation():
 a=assess_delivery(date(2026,11,1),None,False,date(2026,11,15))
 assert a.status=="missing_confirmation" and a.escalation_level==2
 b=assess_delivery(date(2026,10,20),date(2026,11,1),True,date(2026,11,15))
 assert b.status=="overdue" and b.escalation_level==3
def test_reminder_is_approval_gated_draft():
 a=assess_delivery(date(2026,11,1),None,False,date(2026,11,15))
 d=DeliveryAgent().reminder_draft("demo@example.invalid","4500000001",a,"de")
 assert d["requires_approval"] and "verbindlichen Liefertermin" in d["body"]["content"]
