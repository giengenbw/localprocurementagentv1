from __future__ import annotations
import os
from dataclasses import dataclass
@dataclass(frozen=True)
class ConfigIssue:
    level:str; key:str; message:str
def validate_runtime_config(environment:dict[str,str]|None=None)->list[ConfigIssue]:
    env=environment or dict(os.environ); issues=[]
    if env.get("SAP_DRY_RUN","true").lower()!="true":issues.append(ConfigIssue("error","SAP_DRY_RUN","Must remain true until an approved production pilot exists"))
    base=env.get("OLLAMA_BASE_URL","http://127.0.0.1:11434")
    if not any(base.startswith(x) for x in ("http://127.0.0.1","http://localhost")):issues.append(ConfigIssue("warning","OLLAMA_BASE_URL","Non-local Ollama endpoint conflicts with local-first default"))
    if bool(env.get("GRAPH_CLIENT_ID")) != bool(env.get("GRAPH_TENANT_ID")):issues.append(ConfigIssue("error","GRAPH_CLIENT_ID","Tenant ID and client ID must be configured together"))
    if "Mail.Send" in env.get("GRAPH_SCOPES","").split():issues.append(ConfigIssue("warning","GRAPH_SCOPES","Mail.Send is high impact and still requires application approval"))
    return issues
