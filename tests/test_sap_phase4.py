from datetime import date
import pytest
from core.validation import ApprovalStatus,PurchaseRequest
from integrations.sap_gui import MockSAPElement,MockSAPSession,SAPElementMap,SAPElementNotFound,SAPGUIGateway,SAPValidationError
IDS={"transaction_field":"tx","vendor_field":"vendor","purchasing_org_field":"org","purchasing_group_field":"group","company_code_field":"company","item_table":"items","status_bar":"status","save_button":"save"}
class Table(MockSAPElement):
 def set_item_preview(self,item): self.item=item
def session(message_type="S",message="Ready"):
 return MockSAPSession({"tx":MockSAPElement(),"vendor":MockSAPElement(),"org":MockSAPElement(),"group":MockSAPElement(),"company":MockSAPElement(),"items":Table(),"status":MockSAPElement(message,message_type),"save":MockSAPElement()},"MM03")
def request():
 return PurchaseRequest(material_number="MAT-1",quantity=10,unit="ST",delivery_date=date(2026,12,15),supplier_number="100001",plant="1000",purchasing_org="1000",purchasing_group="001")
def test_validate_ids_and_navigate_preview_without_save():
 s=session(); gateway=SAPGUIGateway(IDS,session=s,dry_run=True)
 preview=gateway.preview_po(request())
 assert s.Info.Transaction=="ME21N" and len(preview.validated_element_ids)==7
 gateway.enter_preview_fields(preview)
 assert s.elements["vendor"].Text=="100001"
 assert s.elements["items"].item["material_number"]=="MAT-1"
 assert s.elements["save"].press_count==0
def test_missing_or_changed_id_fails_closed():
 s=session(); del s.elements["vendor"]
 with pytest.raises(SAPElementNotFound): SAPGUIGateway(IDS,session=s).validate_element_ids()
def test_unconfigured_ids_fail_closed():
 with pytest.raises(SAPValidationError): SAPElementMap({"status_bar":"status"}).require_configured()
def test_sap_error_blocks_ready_state():
 preview=SAPGUIGateway(IDS,session=session("E","Vendor missing")).preview_po(request())
 assert not preview.ready_for_manual_save and any("error" in x.lower() for x in preview.messages)
def test_real_save_remains_disabled_even_with_approval():
 gateway=SAPGUIGateway(IDS,session=session(),dry_run=False); preview=gateway.preview_po(request())
 with pytest.raises(NotImplementedError): gateway.save_po(preview,ApprovalStatus.approved)
def test_complete_request_with_success_status_is_ready_for_manual_review():
 preview=SAPGUIGateway(IDS,session=session("S","Ready")).preview_po(request())
 assert preview.ready_for_manual_save

def test_missing_header_fields_are_blocking_warnings():
 req=PurchaseRequest(material_number="MAT-1",quantity=10,unit="ST",delivery_date=date(2026,12,15))
 preview=SAPGUIGateway(IDS,session=session()).preview_po(req)
 assert not preview.ready_for_manual_save
 assert any("supplier_number" in x for x in preview.messages)
