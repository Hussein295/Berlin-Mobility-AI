
from pathlib import Path
import pandas as pd

# Locate the Excel dataset
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "berlin_bicycle_counts.xlsx"
)

# Open the workbook
workbook = pd.ExcelFile(DATA_PATH)

print("\n===== AVAILABLE EXCEL SHEETS =====")

for i, sheet in enumerate(workbook.sheet_names):
    print(f"{i}: {sheet}")

print("\n===== PREVIEW EACH SHEET =====")

for sheet in workbook.sheet_names:
    print(f"\n--- Sheet: {sheet} ---")

    df = pd.read_excel(
        DATA_PATH,
        sheet_name=sheet,
        header=None,
        nrows=8
    )

    # Limit columns so the terminal stays readable
    print(df.iloc[:, :6].to_string(
        index=False,
        header=False
    ))
