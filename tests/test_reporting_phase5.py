from openpyxl import load_workbook
from core.reporting import export_procurement_report
def test_excel_report(tmp_path):
 path=export_procurement_report(str(tmp_path/"report.xlsx"),[{"PO":"4500000001"}],[{"supplier":"Demo","on_time_rate_pct":100}],[{"event":"test"}])
 wb=load_workbook(path)
 assert wb.sheetnames==["Open POs","Supplier KPI","Audit"]
 assert wb["Open POs"].freeze_panes=="A2"
