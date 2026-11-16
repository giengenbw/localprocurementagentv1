from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from core.audit import audit
@dataclass
class JobResult:
    name:str; status:str; started_at:str; finished_at:str; details:dict
class JobRunner:
    def __init__(self,audit_path:str|None=None):self.audit_path=audit_path
    def run(self,name:str,job:Callable[[],dict])->JobResult:
        started=datetime.now(timezone.utc); audit("job_started",details={"job":name},path=self.audit_path)
        try:
            details=job() or {}; status="success"
        except Exception as exc:
            audit("job_failed",details={"job":name,"error":type(exc).__name__},path=self.audit_path); raise
        finished=datetime.now(timezone.utc); audit("job_completed",details={"job":name,"status":status},path=self.audit_path)
        return JobResult(name,status,started.isoformat(),finished.isoformat(),details)
