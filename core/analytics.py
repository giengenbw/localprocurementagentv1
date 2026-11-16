from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from agents.delivery_agent import assess_delivery
@dataclass(frozen=True)
class DashboardKPIs:
    open_pos:int; pending_rfqs:int; missing_confirmations:int; overdue_deliveries:int; pending_approvals:int; average_price_deviation_pct:Decimal

def calculate_kpis(pos:list[dict],pending_rfqs:int=0,pending_approvals:int=0,today:date|None=None)->DashboardKPIs:
    today=today or date.today(); missing=overdue=0; deviations=[]
    for row in pos:
        a=assess_delivery(row["requested_delivery_date"],row.get("confirmed_delivery_date"),row.get("confirmation_received",False),today,row.get("delivered",False))
        missing+=a.status=="missing_confirmation"; overdue+=a.status=="overdue"
        if row.get("price_deviation_pct") is not None: deviations.append(Decimal(str(row["price_deviation_pct"])))
    avg=sum(deviations,Decimal(0))/len(deviations) if deviations else Decimal(0)
    return DashboardKPIs(len([x for x in pos if not x.get("delivered",False)]),pending_rfqs,missing,overdue,pending_approvals,avg)

def supplier_performance(pos:list[dict],today:date|None=None)->list[dict]:
    today=today or date.today(); groups=defaultdict(list)
    for row in pos: groups[row["supplier"]].append(row)
    result=[]
    for supplier,rows in groups.items():
        assessed=[assess_delivery(x["requested_delivery_date"],x.get("confirmed_delivery_date"),x.get("confirmation_received",False),today,x.get("delivered",False)) for x in rows]
        confirmed=[a for a in assessed if a.days_vs_requested is not None]
        on_time=sum(a.days_vs_requested>=0 for a in confirmed)
        result.append({"supplier":supplier,"po_count":len(rows),"confirmation_rate_pct":Decimal(sum(x.get("confirmation_received",False) for x in rows))*100/len(rows),"on_time_rate_pct":Decimal(on_time)*100/len(confirmed) if confirmed else None,"overdue_count":sum(a.status=="overdue" for a in assessed)})
    return sorted(result,key=lambda x:(-x["overdue_count"],x["supplier"]))
