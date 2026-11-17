
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "raw"
    / "berlin_bicycle_counts.xlsx"
)

workbook = pd.ExcelFile(INPUT_FILE)

# Compare an old and a newer year
sheets_to_check = [
    "Jahresdatei 2012",
    "Jahresdatei 2015",
    "Jahresdatei 2022",
    "Jahresdatei 2025",
    "Standortdaten"
]

for sheet in sheets_to_check:

    print(f"\n{'=' * 55}")
    print(f"SHEET: {sheet}")
    print("=" * 55)

    df = pd.read_excel(
        workbook,
        sheet_name=sheet,
        header=None,
        nrows=6
    )

    print("Number of columns:", len(df.columns))

    # Print first six rows and eight columns
    # in a readable way
    for row in range(min(6, len(df))):

        print(f"\nROW {row}:")

        for col in range(min(8, df.shape[1])):

            value = df.iat[row, col]

            print(
                f"  Column {col}: {repr(value)}"
            )

print("\nInspection complete!")
