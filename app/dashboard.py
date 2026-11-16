import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal
from app.chat_interface import render_chat
from agents.quotation_agent import Quote,compare_quotes
from agents.delivery_agent import assess_delivery
from core.analytics import calculate_kpis,supplier_performance
from core.quotation_extraction import extract_quotation_text
st.set_page_config(page_title="Local Procurement AI Agent",layout="wide")
LANG={"Deutsch":{"title":"Beschaffungsübersicht","open":"Offene Bestellungen","rfq":"Offene Anfragen","confirm":"Fehlende Bestätigungen","late":"Überfällige Lieferungen"},"English":{"title":"Procurement Dashboard","open":"Open POs","rfq":"Pending RFQs","confirm":"Missing confirmations","late":"Overdue deliveries"},"中文":{"title":"采购仪表板","open":"未结订单","rfq":"待处理询价","confirm":"缺少订单确认","late":"逾期交货"}}
lang=st.sidebar.selectbox("Language / Sprache / 语言",list(LANG)); t=LANG[lang]
raw=pd.read_csv("data/demo/phase5_open_pos.csv")
raw["requested_delivery_date"]=pd.to_datetime(raw["requested_delivery_date"]).dt.date
raw["confirmed_delivery_date"]=pd.to_datetime(raw["confirmed_delivery_date"],errors="coerce").dt.date
rows=raw.to_dict("records")
for row in rows:
 row["confirmed_delivery_date"]=None if pd.isna(row["confirmed_delivery_date"]) else row["confirmed_delivery_date"]
 row["confirmation_received"]=bool(row["confirmation_received"])
 row["price_deviation_pct"]=None if pd.isna(row["price_deviation_pct"]) else row["price_deviation_pct"]
 a=assess_delivery(row["requested_delivery_date"],row["confirmed_delivery_date"],row["confirmation_received"],date(2026,11,15))
 row.update({"delivery_status":a.status,"difference_days":a.days_vs_requested,"days_overdue":a.days_overdue,"escalation_level":a.escalation_level})
kpi=calculate_kpis(rows,pending_rfqs=4,pending_approvals=2,today=date(2026,11,15))
st.title(t["title"]); cols=st.columns(5)
for box,(label,value) in zip(cols,[(t["open"],kpi.open_pos),(t["rfq"],kpi.pending_rfqs),(t["confirm"],kpi.missing_confirmations),(t["late"],kpi.overdue_deliveries),("Pending approvals",kpi.pending_approvals)]): box.metric(label,value)
st.caption("Synthetic demonstration data only. Difference = requested date - confirmed date; early positive, late negative.")
tab1,tab2,tab3,tab4=st.tabs(["Open POs","Supplier performance","Assistant","Quotation analysis"])
with tab1:
 statuses=st.multiselect("Status",sorted({x["delivery_status"] for x in rows}),default=sorted({x["delivery_status"] for x in rows}))
 st.dataframe(pd.DataFrame([x for x in rows if x["delivery_status"] in statuses]),use_container_width=True,hide_index=True)
with tab2: st.dataframe(pd.DataFrame(supplier_performance(rows,date(2026,11,15))),use_container_width=True,hide_index=True)
with tab3: render_chat()
with tab4:
 sample="""Supplier: Demo GmbH\nQuotation No: Q-77\nMaterial No: DEMO-100\nQuantity: 100\nUnit Price: 12,50\nCurrency: EUR\nMOQ: 50\nDelivery Time: 21 days\nIncoterms: DAP Giengen\nPayment Terms: 30 days net\nValid until: 2027-01-31"""
 text=st.text_area("Quotation text",value=sample,height=220)
 if st.button("Extract quotation"): st.json(extract_quotation_text(text).model_dump(mode="json"))
 qrows=compare_quotes([Quote(supplier="Demo Alpha",material_number="DEMO-100",quantity=100,unit_price=Decimal("12.50"),currency="EUR",moq=50,delivery_days=21),Quote(supplier="Demo Beta",material_number="DEMO-100",quantity=100,unit_price=Decimal("13.10"),currency="EUR",moq=120,delivery_days=14)],Decimal("100"))
 st.dataframe(pd.DataFrame(qrows),use_container_width=True,hide_index=True)
