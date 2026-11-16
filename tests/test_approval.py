import pytest
from core.approval import require_approval
from core.validation import ApprovalStatus
def test_approval_gate():
 with pytest.raises(PermissionError): require_approval(ApprovalStatus.pending,"send")
 require_approval(ApprovalStatus.approved,"send")
