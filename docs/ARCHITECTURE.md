# Architecture

The Phase 1 path is UI/API -> ProcurementAgent -> Ollama JSON extraction -> Pydantic validation -> approval-gated workflow. A deterministic parser provides CPU/offline fallback. Integration boundaries prevent Outlook or SAP side effects from entering the core domain. SAP save and Graph send are denied unless explicit approval is supplied. Real SAP save remains disabled in v0.1.

## Trust boundaries
- User text, email content and attachments are untrusted.
- LLM output is data, validated by Pydantic, never executable code.
- Calculations are deterministic Python.
- Secrets are environment variables and are excluded from Git.
