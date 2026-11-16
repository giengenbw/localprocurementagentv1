from dataclasses import dataclass
from datetime import datetime, timezone
from core.validation import ApprovalStatus
@dataclass(frozen=True)
class ApprovalDecision:
    action: str
    actor: str
    status: ApprovalStatus
    reason: str|None=None
    decided_at: datetime=datetime.now(timezone.utc)
def require_approval(status:ApprovalStatus, action:str)->None:
    if status is not ApprovalStatus.approved: raise PermissionError(f"Explicit approval required for {action}")
