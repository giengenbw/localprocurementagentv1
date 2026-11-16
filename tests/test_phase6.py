import sqlite3
import pytest
from core.auth import Principal,Role,authorize
from core.audit import audit,verify_audit_chain
from core.backup import backup_sqlite
from core.jobs import JobRunner

def test_roles_deny_and_allow():
 authorize(Principal("buyer",Role.buyer),"create_draft")
 with pytest.raises(PermissionError):authorize(Principal("buyer",Role.buyer),"approve_email")
 authorize(Principal("approver",Role.approver),"approve_email")
def test_tamper_evident_audit(tmp_path):
 path=tmp_path/"audit.jsonl"; audit("one",path=str(path)); audit("two",path=str(path))
 assert verify_audit_chain(str(path))==(True,2,None)
 text=path.read_text(); path.write_text(text.replace('"event": "one"','"event": "changed"'))
 assert verify_audit_chain(str(path))[0] is False
def test_consistent_backup_and_retention(tmp_path):
 db=tmp_path/"source.db"; con=sqlite3.connect(db); con.execute("create table demo(id integer)"); con.execute("insert into demo values (1)"); con.commit(); con.close()
 result=backup_sqlite(str(db),str(tmp_path/"backups"),keep=1)
 assert result["integrity"]=="ok"
 assert sqlite3.connect(result["backup"]).execute("select count(*) from demo").fetchone()[0]==1
def test_job_auditing(tmp_path):
 result=JobRunner(str(tmp_path/"audit.jsonl")).run("demo",lambda:{"count":3})
 assert result.status=="success" and result.details["count"]==3
 assert verify_audit_chain(str(tmp_path/"audit.jsonl"))[0]
