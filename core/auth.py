from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class Role(str, Enum):
    viewer="viewer"
    buyer="buyer"
    approver="approver"
    administrator="administrator"

PERMISSIONS={
    Role.viewer:{"read_dashboard","read_audit"},
    Role.buyer:{"read_dashboard","read_audit","create_rfq","create_draft","sap_preview","export_report"},
    Role.approver:{"read_dashboard","read_audit","create_rfq","create_draft","sap_preview","export_report","approve_email","approve_sap"},
    Role.administrator:{"*"},
}
@dataclass(frozen=True)
class Principal:
    username:str
    role:Role

def authorize(principal:Principal, permission:str)->None:
    allowed=PERMISSIONS[principal.role]
    if "*" not in allowed and permission not in allowed:
        raise PermissionError(f"Role '{principal.role.value}' is not permitted to perform '{permission}'")
