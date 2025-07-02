import pandas as pd
from pathlib import Path

xlsx = Path(__file__).resolve().parent.parent / 'spreadsheet' / 'Pricelist_-_ARP_17_June_2025.xlsx'
csv = xlsx.with_suffix('.csv')

pd.read_excel(xlsx, engine='openpyxl').to_csv(csv, index=False, encoding='utf-8')

print(f"✅ Converted {xlsx} to {csv}")