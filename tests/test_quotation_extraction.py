from core.quotation_extraction import extract_quotation_text
def test_extract_structured_quote():
 q=extract_quotation_text("""Supplier: Demo GmbH\nQuotation No: Q-77\nMaterial No: MAT-42\nQuantity: 100\nUnit Price: 12,50\nCurrency: EUR\nMOQ: 50\nDelivery Time: 21 days\nIncoterms: DAP Giengen\nPayment Terms: 30 days net\nValid until: 2027-01-31""")
 assert q.supplier=="Demo GmbH" and q.unit_price==12.5 and q.delivery_days==21
 assert q.missing_fields==[] and len(q.source_hash)==64
def test_missing_fields_are_explicit():
 q=extract_quotation_text("Supplier: Demo GmbH")
 assert set(q.missing_fields)=={"material_number","quantity","unit_price","currency"}
