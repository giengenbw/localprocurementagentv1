from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
from core.approval import require_approval
from core.validation import ApprovalStatus, PurchaseRequest

class SAPElementNotFound(RuntimeError): pass
class SAPValidationError(RuntimeError): pass

class SAPSessionProtocol(Protocol):
    @property
    def Info(self) -> Any: ...
    def findById(self, element_id: str) -> Any: ...
    def StartTransaction(self, transaction: str) -> None: ...

@dataclass
class SAPMessage:
    message_type: str | None
    text: str
    is_error: bool = False

@dataclass
class SAPPreview:
    transaction: str = "ME21N"
    data: dict = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)
    validated_element_ids: list[str] = field(default_factory=list)
    ready_for_manual_save: bool = False

class SAPSessionManager:
    def __init__(self, connection_index: int=0, session_index: int=0):
        self.connection_index=connection_index; self.session_index=session_index
    def connect(self) -> SAPSessionProtocol:
        try:
            import win32com.client
            app=win32com.client.GetObject("SAPGUI").GetScriptingEngine
            return app.Children(self.connection_index).Children(self.session_index)
        except Exception as exc:
            raise RuntimeError("Could not connect to an existing authorized SAP GUI session") from exc

class SAPElementMap:
    REQUIRED_KEYS=("transaction_field","vendor_field","purchasing_org_field","purchasing_group_field","company_code_field","item_table","status_bar")
    def __init__(self, values: dict[str,str]): self.values=values
    @classmethod
    def from_config(cls, config:dict): return cls(config.get("me21n",config))
    def require_configured(self, keys:tuple[str,...]|None=None):
        keys=keys or self.REQUIRED_KEYS
        missing=[k for k in keys if not self.values.get(k)]
        if missing: raise SAPValidationError(f"SAP element IDs are not configured: {', '.join(missing)}")
    def validate_exists(self, session:SAPSessionProtocol, keys:tuple[str,...]|None=None)->list[str]:
        keys=keys or self.REQUIRED_KEYS; self.require_configured(keys); validated=[]
        for key in keys:
            element_id=self.values[key]
            try: session.findById(element_id)
            except Exception as exc: raise SAPElementNotFound(f"SAP element '{key}' not found at '{element_id}'") from exc
            validated.append(element_id)
        return validated

class SAPGateway:
    def preview_po(self,request:PurchaseRequest)->SAPPreview: raise NotImplementedError
    def save_po(self,preview:SAPPreview,approval:ApprovalStatus)->str: raise NotImplementedError

class MockSAPElement:
    def __init__(self,text="",message_type="S"): self.text=text; self.Text=text; self.MessageType=message_type; self.press_count=0
    def press(self): self.press_count+=1

class MockSAPInfo:
    def __init__(self,transaction=""): self.Transaction=transaction

class MockSAPSession:
    def __init__(self,elements:dict[str,MockSAPElement]|None=None,transaction=""):
        self.elements=elements or {}; self.Info=MockSAPInfo(transaction); self.started=[]
    def findById(self,element_id):
        if element_id not in self.elements: raise KeyError(element_id)
        return self.elements[element_id]
    def StartTransaction(self,transaction): self.Info.Transaction=transaction; self.started.append(transaction)

class MockSAPGateway(SAPGateway):
    def preview_po(self,request):
        if request.missing_required(): raise SAPValidationError(f"Request is incomplete: {', '.join(request.missing_required())}")
        return SAPPreview(data=request.model_dump(mode="json"),messages=["DRY RUN: no SAP transaction executed"],ready_for_manual_save=False)
    def save_po(self,preview,approval):
        require_approval(approval,"SAP purchase order save")
        return "MOCK-PO-NOT-CREATED"

class SAPGUIGateway(SAPGateway):
    """ME21N preview integration. Real save remains intentionally disabled in v0.4."""
    def __init__(self, element_ids:dict, dry_run:bool=True, session:SAPSessionProtocol|None=None, session_manager:SAPSessionManager|None=None):
        self.map=SAPElementMap.from_config(element_ids); self.dry_run=dry_run; self.session=session; self.manager=session_manager or SAPSessionManager()
    def connect(self):
        self.session=self.session or self.manager.connect(); return self.session
    def _session(self): return self.session or self.connect()
    def current_transaction(self): return getattr(self._session().Info,"Transaction",None)
    def navigate_me21n(self):
        s=self._session()
        if self.current_transaction()!="ME21N": s.StartTransaction("ME21N")
        return self.current_transaction()
    def validate_element_ids(self,keys:tuple[str,...]|None=None): return self.map.validate_exists(self._session(),keys)
    def read_status_message(self)->SAPMessage:
        self.map.require_configured(("status_bar",)); bar=self._session().findById(self.map.values["status_bar"])
        text=getattr(bar,"Text",getattr(bar,"text","")); typ=getattr(bar,"MessageType",None)
        return SAPMessage(typ,text,typ in {"E","A","X"})
    def preview_po(self,request):
        missing=request.missing_required()
        if missing: raise SAPValidationError(f"Request is incomplete: {', '.join(missing)}")
        validated=self.validate_element_ids()
        self.navigate_me21n()
        msg=self.read_status_message()
        data={"header":{"supplier_number":request.supplier_number,"purchasing_org":request.purchasing_org,"purchasing_group":request.purchasing_group,"plant":request.plant},"items":[{"material_number":request.material_number,"quantity":str(request.quantity),"unit":request.unit,"delivery_date":str(request.delivery_date),"net_price":str(request.net_price) if request.net_price is not None else None,"currency":request.currency}]}
        warnings=[]
        for key in ("supplier_number","purchasing_org","purchasing_group","plant"):
            if data["header"][key] is None: warnings.append(f"Header field '{key}' requires buyer/SAP validation")
        blocking_warnings=bool(warnings)
        if msg.text: warnings.append(f"SAP status [{msg.message_type or '-'}]: {msg.text}")
        if msg.is_error: warnings.append("SAP reports an error; preview is not ready")
        return SAPPreview(data=data,messages=warnings,validated_element_ids=validated,ready_for_manual_save=not msg.is_error and not blocking_warnings)
    def enter_preview_fields(self,preview:SAPPreview):
        """Populate only configured fields for buyer inspection. Does not press Save."""
        s=self._session(); self.map.require_configured()
        header=preview.data["header"]; item=preview.data["items"][0]
        field_values={"vendor_field":header.get("supplier_number"),"purchasing_org_field":header.get("purchasing_org"),"purchasing_group_field":header.get("purchasing_group"),"company_code_field":None}
        for key,value in field_values.items():
            if value is not None: s.findById(self.map.values[key]).Text=str(value)
        table=s.findById(self.map.values["item_table"])
        if hasattr(table,"set_item_preview"): table.set_item_preview(item)
        else: preview.messages.append("Item table adapter is site-specific; item values were not written")
        return self.read_status_message()
    def save_po(self,preview,approval):
        require_approval(approval,"real SAP purchase order save")
        if self.dry_run: raise PermissionError("SAP_DRY_RUN is enabled")
        raise NotImplementedError("v0.4 intentionally forbids automated saving of real purchase orders")
