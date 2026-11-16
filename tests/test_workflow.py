from core.validation import PurchaseRequest
from core.workflow import build_plan
def test_questions_for_missing_fields():
 p=build_plan(PurchaseRequest(material_number="123",language="de"))
 assert set(p.missing_fields)=={"quantity","unit","delivery_date"}; assert not p.ready_for_sap_preview
