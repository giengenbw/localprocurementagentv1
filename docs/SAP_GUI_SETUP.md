# SAP GUI Scripting deployment checklist

1. Obtain written authorization from SAP Basis and information security. The application never bypasses SAP roles or authorizations.
2. Enable SAP GUI Scripting on the approved SAP application server and in SAP GUI for Windows. Keep SAP audit and authorization controls active.
3. Use an already authenticated SAP GUI session. Password handling is outside this project.
4. Copy `config/sap_element_ids.example.yaml` to a local, git-ignored configuration and record IDs with SAP GUI Script Recording and Playback.
5. Validate every ID against the exact SAP GUI version, theme, language, user layout and ME21N screen variant. IDs can change after SAP upgrades or personalization.
6. Run mock tests first. Then execute preview-only tests in a designated SAP quality system with synthetic/test master data.
7. Keep `SAP_DRY_RUN=true`. Version 0.4 does not implement automated Save, even after approval.
8. Review the SAP status bar. Types `E`, `A` and `X` block readiness. Never infer success only from screen navigation.
9. Establish a four-eyes process before any future production pilot: requester, buyer/approver, PO preview, field reconciliation, final manual Save.
