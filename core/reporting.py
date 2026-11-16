from __future__ import annotations
from pathlib import Path
from copy import copy
import pandas as pd

def export_procurement_report(path:str,open_pos:list[dict],supplier_kpis:list[dict],audit_rows:list[dict]|None=None)->str:
    target=Path(path)
    if target.suffix.lower()!=".xlsx": raise ValueError("Report path must end with .xlsx")
    target.parent.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(target,engine="openpyxl") as writer:
        pd.DataFrame(open_pos).to_excel(writer,sheet_name="Open POs",index=False)
        pd.DataFrame(supplier_kpis).to_excel(writer,sheet_name="Supplier KPI",index=False)
        pd.DataFrame(audit_rows or []).to_excel(writer,sheet_name="Audit",index=False)
        for ws in writer.book.worksheets:
            ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions
            for cell in ws[1]: font=copy(cell.font); font.bold=True; cell.font=font
            for column in ws.columns:
                width=min(max(len(str(c.value or "")) for c in column)+2,45)
                ws.column_dimensions[column[0].column_letter].width=width
    return str(target)
