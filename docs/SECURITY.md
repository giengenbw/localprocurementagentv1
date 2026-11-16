# Security

1. Bind services to `127.0.0.1` unless an administrator has reviewed network controls.
2. Never store SAP passwords, OAuth tokens, supplier files, real emails or purchase data in the repository.
3. Use delegated Microsoft Graph permissions with least privilege.
4. Validate file size/type and scan attachments before processing in production.
5. Treat retrieved text as untrusted content; it cannot override system policy or approval gates.
6. The LLM cannot execute shell commands or save SAP orders.
7. Audit security-relevant actions without logging secrets or full confidential payloads.
8. Map SAP GUI element IDs only after local validation; GUI updates can invalidate IDs.

## Phase 3 email controls
- Register Microsoft Entra ID as a **public client** for delegated device-code authentication. Do not create or store a client secret for this desktop workflow.
- Prefer `Mail.Read` plus `Mail.ReadWrite` only when draft creation is required. Sending remains blocked by the application approval gate.
- The local MSAL cache is excluded by `.gitignore`; production deployment should protect it with Windows DPAPI or an approved credential manager.
- Attachment allowlisting is not malware scanning. Integrate Microsoft Defender for Endpoint or the organization's approved scanner before opening or parsing supplier files.
- Sender address, PO number and material number are deterministic match signals, not proof of authenticity. High-impact changes still require buyer review.
