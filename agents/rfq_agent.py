from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from database.models import RFQStatus, RFQSupplier
from database.repositories import RFQRepository, SupplierRepository

@dataclass
class RFQDraft:
    subject: str
    body: str
    deadline: date
    requires_approval: bool = True

class RFQAgent:
    def __init__(self, session: Session | None=None): self.session=session
    def draft(self, material: str, quantity: float, unit: str, deadline: date, language="de", description: str|None=None):
        desc=f" ({description})" if description else ""
        if language=="de": return RFQDraft(f"Anfrage: {material}",f"Bitte senden Sie uns Ihr Angebot für {quantity:g} {unit} Material {material}{desc}. Angebotsfrist: {deadline:%d.%m.%Y}.",deadline)
        if language=="zh": return RFQDraft(f"询价：{material}",f"请为物料 {material}{desc}，数量 {quantity:g} {unit} 提供报价。报价截止日期：{deadline:%Y-%m-%d}。",deadline)
        return RFQDraft(f"RFQ: {material}",f"Please quote {quantity:g} {unit} of material {material}{desc}. Quotation deadline: {deadline:%Y-%m-%d}.",deadline)
    def create_rfq(self, rfq_number: str, material_number: str, quantity: Decimal, unit: str, quotation_deadline: date, supplier_ids: list[int], requested_delivery_date: date|None=None, description: str|None=None, created_by="local-user"):
        if not self.session: raise RuntimeError("Database session required")
        if not supplier_ids: raise ValueError("At least one supplier is required")
        rfq=RFQRepository(self.session).create(rfq_number=rfq_number,material_number=material_number,quantity=quantity,unit=unit,quotation_deadline=quotation_deadline,requested_delivery_date=requested_delivery_date,description=description,status=RFQStatus.waiting_approval.value,created_by=created_by)
        suppliers=SupplierRepository(self.session)
        for sid in supplier_ids:
            supplier=suppliers.get(sid)
            if not supplier or not supplier.active: raise ValueError(f"Unknown or inactive supplier id: {sid}")
            d=self.draft(material_number,float(quantity),unit,quotation_deadline,supplier.preferred_language,description)
            self.session.add(RFQSupplier(rfq_id=rfq.id,supplier_id=sid,draft_subject=d.subject,draft_body=d.body))
        self.session.flush(); return rfq
