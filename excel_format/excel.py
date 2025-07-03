import re
import pandas as pd
from pathlib import Path

def convert_xlsx_to_csv():
    xlsx = Path(__file__).resolve().parent.parent / 'spreadsheet' / 'Pricelist_-_ARP_17_June_2025.xlsx'
    csv = xlsx.with_suffix('.csv')
    pd.read_excel(xlsx, engine='openpyxl').to_csv(csv, index=False, encoding='utf-8')
    print(f"✅ Converted {xlsx} to {csv}")

def extract_matching_rows_from_xlsx():
    xlsx = Path(__file__).resolve().parent.parent / 'spreadsheet' / 'Pricelist_-_ARP_17_June_2025.xlsx'
    df = pd.read_excel(xlsx, engine='openpyxl', header=None, dtype=str)
    pattern = r'^[A-Z0-9/-]*[0-9][A-Z0-9/-]*$'
    matching_rows = df[df[0].apply(lambda x: bool(re.match(pattern, str(x))) if pd.notnull(x) else False)]
    output_xlsx = xlsx.parent / 'Pricelist_-_ARP_17_June_2025_formatted.xlsx'
    matching_rows.to_excel(output_xlsx, index=False, header=False, engine='openpyxl')
    print(f"✅ Formatted spreadsheet saved to {output_xlsx}")

if __name__ == "__main__":
    convert_xlsx_to_csv()
    extract_matching_rows_from_xlsx()