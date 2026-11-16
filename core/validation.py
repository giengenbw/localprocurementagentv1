from __future__ import annotations
from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Language(str, Enum): de="de"; en="en"; zh="zh"
class ApprovalStatus(str, Enum): pending="pending"; approved="approved"; rejected="rejected"

class PurchaseRequest(BaseModel):
    model_config=ConfigDict(extra="forbid", str_strip_whitespace=True)
    material_number: str|None=None
    quantity: Decimal|None=Field(default=None, gt=0)
    unit: str|None=None
    delivery_date: date|None=None
    supplier_number: str|None=None
    plant: str|None=None
    purchasing_org: str|None=None
    purchasing_group: str|None=None
    net_price: Decimal|None=Field(default=None, ge=0)
    currency: str|None=None
    language: Language=Language.de
    @field_validator("material_number","supplier_number")
    @classmethod
    def identifiers(cls,v):
        if v is not None and not v.replace("-","").isalnum(): raise ValueError("identifier contains invalid characters")
        return v
    def missing_required(self)->list[str]:
        required=("material_number","quantity","unit","delivery_date")
        return [x for x in required if getattr(self,x) is None]

class WorkflowStep(BaseModel):
    name: str
    status: str="pending"
    requires_approval: bool=False

class ProcurementPlan(BaseModel):
    request: PurchaseRequest
    missing_fields: list[str]
    clarification_questions: list[str]
    steps: list[WorkflowStep]
    ready_for_sap_preview: bool=False
