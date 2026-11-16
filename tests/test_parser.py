from core.parser import deterministic_extract
def test_german_request():
 r=deterministic_extract("Erstelle eine Bestellung für Material 123456, 10 Stück, Liefertermin 15.12.2026.")
 assert r.material_number=="123456" and r.quantity==10 and r.unit=="ST"
 assert str(r.delivery_date)=="2026-12-15"
def test_missing_not_invented():
 r=deterministic_extract("Bitte Bestellung erstellen")
 assert r.material_number is None and r.supplier_number is None and r.net_price is None
