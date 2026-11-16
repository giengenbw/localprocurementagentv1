from __future__ import annotations
import argparse,json
from core.backup import backup_sqlite
from core.jobs import JobRunner

def main():
    parser=argparse.ArgumentParser(description="Run local procurement maintenance jobs")
    parser.add_argument("--database",default="data/procurement.db")
    parser.add_argument("--backup-dir",default="data/backups")
    parser.add_argument("--keep",type=int,default=14)
    args=parser.parse_args()
    runner=JobRunner()
    result=runner.run("daily_backup",lambda:backup_sqlite(args.database,args.backup_dir,args.keep))
    print(json.dumps(result.__dict__,indent=2))
if __name__=="__main__":main()
