from integrations.sap_gui import MockSAPGateway
from core.validation import PurchaseRequest,ApprovalStatus
def test_mock_never_creates_real_po():
 sap=MockSAPGateway(); preview=sap.preview_po(PurchaseRequest(material_number="1",quantity=1,unit="ST",delivery_date="2026-12-15"))
 assert "DRY RUN" in preview.messages[0]
 assert sap.save_po(preview,ApprovalStatus.approved)=="MOCK-PO-NOT-CREATED"
