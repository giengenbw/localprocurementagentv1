from __future__ import annotations
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Quotation, RFQ, RFQStatus, Supplier

class SupplierRepository:
    def __init__(self, session: Session): self.session = session
    def create(self, **values) -> Supplier:
        row = Supplier(**values); self.session.add(row); self.session.flush(); return row
    def get(self, supplier_id: int) -> Supplier | None: return self.session.get(Supplier, supplier_id)
    def by_number(self, number: str) -> Supplier | None:
        return self.session.scalar(select(Supplier).where(Supplier.supplier_number == number))
    def search(self, term: str) -> list[Supplier]:
        return list(self.session.scalars(select(Supplier).where(Supplier.name.ilike(f"%{term}%")).order_by(Supplier.name)))

class RFQRepository:
    def __init__(self, session: Session): self.session = session
    def create(self, **values) -> RFQ:
        row = RFQ(**values); self.session.add(row); self.session.flush(); return row
    def get(self, rfq_id: int) -> RFQ | None: return self.session.get(RFQ, rfq_id)
    def pending(self, as_of: date) -> list[RFQ]:
        stmt = select(RFQ).where(RFQ.quotation_deadline >= as_of, RFQ.status.not_in([RFQStatus.completed.value, RFQStatus.cancelled.value])).order_by(RFQ.quotation_deadline)
        return list(self.session.scalars(stmt))

class QuotationRepository:
    def __init__(self, session: Session): self.session = session
    def create(self, **values) -> Quotation:
        row=Quotation(**values); self.session.add(row); self.session.flush(); return row
    def for_rfq(self, rfq_id: int) -> list[Quotation]:
        stmt=select(Quotation).where(Quotation.rfq_id==rfq_id).order_by(Quotation.unit_price)
        return list(self.session.scalars(stmt))
    def historical(self, material_number: str, supplier_id: int | None=None, limit: int=10) -> list[Quotation]:
        stmt=select(Quotation).where(Quotation.material_number==material_number)
        if supplier_id is not None: stmt=stmt.where(Quotation.supplier_id==supplier_id)
        return list(self.session.scalars(stmt.order_by(Quotation.created_at.desc()).limit(limit)))

from database.models import ApprovalRecord, OpenPurchaseOrder, DeliveryEvent

class PurchaseOrderRepository:
    def __init__(self, session: Session): self.session=session
    def create(self, **values) -> OpenPurchaseOrder:
        row=OpenPurchaseOrder(**values); self.session.add(row); self.session.flush(); return row
    def get_by_number(self, po_number:str) -> OpenPurchaseOrder|None:
        return self.session.scalar(select(OpenPurchaseOrder).where(OpenPurchaseOrder.po_number==po_number))
    def open(self) -> list[OpenPurchaseOrder]:
        return list(self.session.scalars(select(OpenPurchaseOrder).where(OpenPurchaseOrder.status=="open").order_by(OpenPurchaseOrder.requested_delivery_date)))
    def add_event(self, purchase_order_id:int, **values) -> DeliveryEvent:
        row=DeliveryEvent(purchase_order_id=purchase_order_id,**values); self.session.add(row); self.session.flush(); return row

class ApprovalRepository:
    def __init__(self, session: Session): self.session=session
    def pending(self) -> list[ApprovalRecord]:
        return list(self.session.scalars(select(ApprovalRecord).where(ApprovalRecord.status=="pending").order_by(ApprovalRecord.created_at)))
