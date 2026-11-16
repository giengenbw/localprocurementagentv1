from __future__ import annotations
import json, os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import httpx
from core.approval import require_approval
from core.validation import ApprovalStatus

GRAPH_ROOT = "https://graph.microsoft.com/v1.0"

class TokenProvider(Protocol):
    def access_token(self) -> str: ...

class MSALDeviceCodeTokenProvider:
    """Delegated OAuth2 device-code provider. Token cache stays local and is git-ignored."""
    def __init__(self, tenant_id: str, client_id: str, scopes: list[str], cache_path: str="data/msal_token_cache.json"):
        if not tenant_id or not client_id:
            raise ValueError("GRAPH_TENANT_ID and GRAPH_CLIENT_ID are required")
        self.tenant_id, self.client_id, self.scopes = tenant_id, client_id, scopes
        self.cache_path = Path(cache_path)
    def access_token(self) -> str:
        try:
            import msal
        except ImportError as exc:
            raise RuntimeError("Install the 'msal' package to use Microsoft Graph authentication") from exc
        cache=msal.SerializableTokenCache()
        if self.cache_path.exists(): cache.deserialize(self.cache_path.read_text(encoding="utf-8"))
        app=msal.PublicClientApplication(self.client_id,authority=f"https://login.microsoftonline.com/{self.tenant_id}",token_cache=cache)
        accounts=app.get_accounts()
        result=app.acquire_token_silent(self.scopes,account=accounts[0] if accounts else None)
        if not result:
            flow=app.initiate_device_flow(scopes=self.scopes)
            if "user_code" not in flow: raise RuntimeError(f"Could not start device flow: {flow}")
            print(flow["message"])
            result=app.acquire_token_by_device_flow(flow)
        if cache.has_state_changed:
            self.cache_path.parent.mkdir(parents=True,exist_ok=True)
            self.cache_path.write_text(cache.serialize(),encoding="utf-8")
        token=result.get("access_token")
        if not token: raise RuntimeError(result.get("error_description","Microsoft authentication failed"))
        return token

class GraphClient:
    def __init__(self, token_provider: TokenProvider, transport: httpx.BaseTransport|None=None, timeout: float=30):
        self.tokens=token_provider; self.transport=transport; self.timeout=timeout
    def _request(self, method: str, path: str, **kwargs):
        headers={"Authorization":f"Bearer {self.tokens.access_token()}","Accept":"application/json"}
        if "json" in kwargs: headers["Content-Type"]="application/json"
        with httpx.Client(base_url=GRAPH_ROOT,headers=headers,timeout=self.timeout,transport=self.transport) as client:
            response=client.request(method,path,**kwargs)
        response.raise_for_status()
        return response.json() if response.content else None
    def list_messages(self, top=20):
        top=max(1,min(int(top),100))
        params={"$top":top,"$select":"id,subject,from,receivedDateTime,bodyPreview,hasAttachments","$orderby":"receivedDateTime desc"}
        return self._request("GET","/me/messages",params=params).get("value",[])
    def get_message(self,message_id:str):
        return self._request("GET",f"/me/messages/{message_id}",params={"$select":"id,subject,from,toRecipients,receivedDateTime,body,bodyPreview,hasAttachments"})
    def list_attachments(self,message_id:str):
        return self._request("GET",f"/me/messages/{message_id}/attachments").get("value",[])
    def create_draft(self,message:dict): return self._request("POST","/me/messages",json=message)
    def send_draft(self,draft_id:str): return self._request("POST",f"/me/messages/{draft_id}/send")

@dataclass
class MockGraphClient:
    messages: list[dict]
    drafts: list[dict]
    sent_ids: list[str]
    def list_messages(self,top=20): return self.messages[:top]
    def get_message(self,message_id): return next(x for x in self.messages if x["id"]==message_id)
    def list_attachments(self,message_id): return next((x.get("attachments",[]) for x in self.messages if x["id"]==message_id),[])
    def create_draft(self,message):
        row={"id":f"draft-{len(self.drafts)+1}",**message}; self.drafts.append(row); return row
    def send_draft(self,draft_id): self.sent_ids.append(draft_id); return None

class OutlookGateway:
    def __init__(self,client=None): self.client=client
    @classmethod
    def from_env(cls):
        scopes=os.getenv("GRAPH_SCOPES","Mail.Read Mail.ReadWrite User.Read offline_access").split()
        token=MSALDeviceCodeTokenProvider(os.getenv("GRAPH_TENANT_ID",""),os.getenv("GRAPH_CLIENT_ID",""),scopes)
        return cls(GraphClient(token))
    def list_messages(self,top=20):
        if self.client is None: raise RuntimeError("Microsoft Graph client not configured")
        return self.client.list_messages(top=top)
    def get_message(self,message_id):
        if self.client is None: raise RuntimeError("Microsoft Graph client not configured")
        return self.client.get_message(message_id)
    def list_attachments(self,message_id):
        if self.client is None: raise RuntimeError("Microsoft Graph client not configured")
        return self.client.list_attachments(message_id)
    def create_draft(self,message:dict):
        if self.client is None: raise RuntimeError("Microsoft Graph client not configured")
        return self.client.create_draft(message)
    def send(self,draft_id:str,approval:ApprovalStatus):
        require_approval(approval,"external email send")
        if self.client is None: raise RuntimeError("Microsoft Graph client not configured")
        return self.client.send_draft(draft_id)
