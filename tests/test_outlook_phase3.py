import base64
import httpx, pytest
from core.validation import ApprovalStatus
from integrations.outlook import GraphClient, MockGraphClient, OutlookGateway
from integrations.attachment_security import assess_attachment,decode_graph_attachment
class Token:
 def access_token(self): return "test-token"
def test_graph_request_and_fields():
 def handler(req):
  assert req.headers["Authorization"]=="Bearer test-token"
  return httpx.Response(200,json={"value":[{"id":"1","subject":"Demo"}]})
 rows=GraphClient(Token(),transport=httpx.MockTransport(handler)).list_messages(5)
 assert rows[0]["subject"]=="Demo"
def test_draft_send_requires_approval():
 mock=MockGraphClient([],[],[]); gateway=OutlookGateway(mock)
 draft=gateway.create_draft({"subject":"Synthetic"})
 with pytest.raises(PermissionError): gateway.send(draft["id"],ApprovalStatus.pending)
 gateway.send(draft["id"],ApprovalStatus.approved)
 assert mock.sent_ids==[draft["id"]]
def test_attachment_allowlist_and_signature():
 content=b"synthetic pdf text"; item={"contentBytes":base64.b64encode(content).decode()}
 assert decode_graph_attachment(item)==content
 assert assess_attachment("quote.pdf",content).safe_for_extraction
 assert not assess_attachment("quote.exe",content).safe_for_extraction
 assert not assess_attachment("quote.pdf",b"MZmalware").safe_for_extraction
