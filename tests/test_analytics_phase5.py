from datetime import date
from decimal import Decimal
from core.analytics import calculate_kpis,supplier_performance
ROWS=[{"supplier":"A","requested_delivery_date":date(2026,11,1),"confirmed_delivery_date":date(2026,11,5),"confirmation_received":True,"price_deviation_pct":4},{"supplier":"A","requested_delivery_date":date(2026,12,1),"confirmed_delivery_date":date(2026,12,1),"confirmation_received":True,"price_deviation_pct":2},{"supplier":"B","requested_delivery_date":date(2026,12,1),"confirmed_delivery_date":None,"confirmation_received":False}]
def test_kpis_are_deterministic():
 k=calculate_kpis(ROWS,2,3,date(2026,11,15))
 assert k.open_pos==3 and k.overdue_deliveries==1 and k.missing_confirmations==1
 assert k.average_price_deviation_pct==Decimal("3")
def test_supplier_performance():
 result=supplier_performance(ROWS,date(2026,11,15))
 a=next(x for x in result if x["supplier"]=="A")
 assert a["confirmation_rate_pct"]==100 and a["on_time_rate_pct"]==50
