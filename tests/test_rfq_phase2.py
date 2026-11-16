from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.orm import sessionmaker
from agents.rfq_agent import RFQAgent
from database.db import create_db_engine, init_db
from database.repositories import SupplierRepository

def test_persist_rfq_with_multilingual_drafts():
 e=create_db_engine("sqlite:///:memory:"); init_db(e); S=sessionmaker(bind=e,expire_on_commit=False)
 with S.begin() as s:
  de=SupplierRepository(s).create(name="Demo DE",supplier_number="D1",preferred_language="de")
  zh=SupplierRepository(s).create(name="Demo ZH",supplier_number="Z1",preferred_language="zh")
  rfq=RFQAgent(s).create_rfq("RFQ-2","MAT-1",Decimal("5"),"ST",date(2027,1,10),[de.id,zh.id])
  assert len(rfq.invitations)==2
  assert "Anfrage" in rfq.invitations[0].draft_subject
  assert "询价" in rfq.invitations[1].draft_subject
