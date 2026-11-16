from datetime import date
from decimal import Decimal
from sqlalchemy.orm import sessionmaker
from database.db import create_db_engine, init_db
from database.repositories import QuotationRepository, RFQRepository, SupplierRepository

def factory():
 e=create_db_engine("sqlite:///:memory:"); init_db(e); return sessionmaker(bind=e,expire_on_commit=False)
def test_supplier_rfq_and_history():
 S=factory()
 with S.begin() as s:
  supplier=SupplierRepository(s).create(name="Synthetic Supplier",supplier_number="SYN-1",email="demo@example.invalid")
  rfq=RFQRepository(s).create(rfq_number="RFQ-1",material_number="DEMO-1",quantity=Decimal("10"),unit="ST",quotation_deadline=date(2027,1,1))
  QuotationRepository(s).create(rfq_id=rfq.id,supplier_id=supplier.id,quote_reference="Q-1",material_number="DEMO-1",quantity=10,unit_price=12,currency="EUR")
 with S() as s:
  assert RFQRepository(s).pending(date(2026,1,1))[0].rfq_number=="RFQ-1"
  assert QuotationRepository(s).historical("DEMO-1")[0].quote_reference=="Q-1"
