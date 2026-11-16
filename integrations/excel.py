import pandas as pd
def export_comparison(rows:list[dict],path:str)->str:
    pd.DataFrame(rows).to_excel(path,index=False,engine="openpyxl"); return path
