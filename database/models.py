from __future__ import annotations
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class RFQStatus(str, Enum):
    draft = "draft"
    waiting_approval = "waiting_approval"
    sent = "sent"
    partially_quoted = "partially_quoted"
    completed = "completed"
    cancelled = "cancelled"

class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    supplier_number: Mapped[str | None] = mapped_column(String(40), unique=True)
    email: Mapped[str | None] = mapped_column(String(320))
    country_code: Mapped[str | None] = mapped_column(String(2))
    preferred_language: Mapped[str] = mapped_column(String(2), default="de")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    quotations: Mapped[list[Quotation]] = relationship(back_populates="supplier")

class RFQ(Base):
    __tablename__ = "rfqs"
    id: Mapped[int] = mapped_column(primary_key=True)
    rfq_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    material_number: Mapped[str] = mapped_column(String(60), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    unit: Mapped[str] = mapped_column(String(10))
    requested_delivery_date: Mapped[date | None] = mapped_column(Date)
    quotation_deadline: Mapped[date] = mapped_column(Date, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[str] = mapped_column(String(30), default=RFQStatus.draft.value, index=True)
    created_by: Mapped[str] = mapped_column(String(120), default="local-user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    invitations: Mapped[list[RFQSupplier]] = relationship(back_populates="rfq", cascade="all, delete-orphan")
    quotations: Mapped[list[Quotation]] = relationship(back_populates="rfq", cascade="all, delete-orphan")

class RFQSupplier(Base):
    __tablename__ = "rfq_suppliers"
    __table_args__ = (UniqueConstraint("rfq_id", "supplier_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    rfq_id: Mapped[int] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"))
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    draft_subject: Mapped[str | None] = mapped_column(String(300))
    draft_body: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rfq: Mapped[RFQ] = relationship(back_populates="invitations")
    supplier: Mapped[Supplier] = relationship()

class Quotation(Base):
    __tablename__ = "quotations"
    __table_args__ = (UniqueConstraint("rfq_id", "supplier_id", "quote_reference"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    rfq_id: Mapped[int] = mapped_column(ForeignKey("rfqs.id", ondelete="CASCADE"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    quote_reference: Mapped[str] = mapped_column(String(100))
    material_number: Mapped[str] = mapped_column(String(60), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    currency: Mapped[str] = mapped_column(String(3))
    moq: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    delivery_days: Mapped[int | None] = mapped_column(Integer)
    promised_delivery_date: Mapped[date | None] = mapped_column(Date)
    incoterms: Mapped[str | None] = mapped_column(String(30))
    payment_terms: Mapped[str | None] = mapped_column(String(200))
    validity_date: Mapped[date | None] = mapped_column(Date)
    source_hash: Mapped[str | None] = mapped_column(String(64))
    extraction_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    rfq: Mapped[RFQ] = relationship(back_populates="quotations")
    supplier: Mapped[Supplier] = relationship(back_populates="quotations")

class ApprovalRecord(Base):
    __tablename__ = "approval_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(100))
    actor: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class OpenPurchaseOrder(Base):
    __tablename__ = "open_purchase_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    po_number: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), index=True)
    material_number: Mapped[str] = mapped_column(String(60), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3))
    unit: Mapped[str] = mapped_column(String(10))
    net_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    currency: Mapped[str | None] = mapped_column(String(3))
    requested_delivery_date: Mapped[date] = mapped_column(Date, index=True)
    sap_delivery_date: Mapped[date | None] = mapped_column(Date)
    confirmed_delivery_date: Mapped[date | None] = mapped_column(Date)
    confirmation_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="open", index=True)
    buyer: Mapped[str | None] = mapped_column(String(120), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    supplier: Mapped[Supplier] = relationship()

class DeliveryEvent(Base):
    __tablename__ = "delivery_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("open_purchase_orders.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    event_date: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(50))
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
