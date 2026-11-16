# Local operations runbook

## Daily task
Use `install_scheduled_task.ps1` from an elevated PowerShell only after reviewing the task definition. The default schedule is 06:00 local time and performs an online SQLite backup with `PRAGMA integrity_check`. It retains 14 backups.

## Recovery drill
1. Stop FastAPI and Streamlit.
2. Copy `data/procurement.db` aside.
3. Copy a selected `data/backups/procurement-*.db` to `data/procurement.db`.
4. Run `python -c "import sqlite3; print(sqlite3.connect('data/procurement.db').execute('PRAGMA integrity_check').fetchone())"`.
5. Start the API and verify `/health` and `/api/system/health`.

## Role model
- `viewer`: read dashboard/audit
- `buyer`: create RFQ/drafts, SAP preview, report export
- `approver`: buyer abilities plus email/SAP approval
- `administrator`: all permissions

The application role does not replace SAP or Microsoft Entra authorization.

## Incident handling
Preserve the append-only audit JSONL and database backup. Do not email logs externally because they may contain operational metadata. Verify the audit hash chain before analysis.
