
from pathlib import Path
import re
import pandas as pd

# =====================================
# 1. PROJECT PATHS
# =====================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "data" / "raw"
    / "berlin_bicycle_counts.xlsx"
)

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =====================================
# 2. OPEN EXCEL WORKBOOK
# =====================================

workbook = pd.ExcelFile(INPUT_FILE)

yearly_sheets = sorted(
    [
        name for name in workbook.sheet_names
        if re.fullmatch(
            r"Jahresdatei[_ ]\d{4}",
            name
        )
    ],
    key=lambda name: int(name[-4:])
)

print("Yearly sheets found:", yearly_sheets)

# =====================================
# 3. LOAD STATION METADATA
# =====================================

stations = pd.read_excel(
    workbook,
    sheet_name="Standortdaten"
)

stations = stations.rename(columns={
    "Zählstelle": "station_id",
    "Beschreibung - Fahrtrichtung": "station_name",
    "Breitengrad": "latitude",
    "Längengrad": "longitude",
    "Installationsdatum": "installation_date"
})

stations["station_id"] = (
    stations["station_id"]
    .astype("string")
    .str.strip()
)

stations["installation_date"] = pd.to_datetime(
    stations["installation_date"],
    errors="coerce"
)

stations = stations.dropna(
    subset=["station_id"]
)

stations.to_csv(
    OUTPUT_DIR / "berlin_stations.csv",
    index=False
)

print("Metadata stations:", len(stations))

# =====================================
# 4. EXTRACT STATION IDENTIFIERS
# =====================================

def extract_station_id(header):
    """
    Example:
    '02-MI-JAN-N 01.04.2015'
    -> '02-MI-JAN-N'

    '01-MI-AL-W\\n16.12.2021'
    -> '01-MI-AL-W'
    """

    if pd.isna(header):
        return None

    text = str(header).strip().upper()

    match = re.match(
        r"^(\d{2}-[A-Z]{2}-[A-Z0-9]+"
        r"(?:-[A-Z0-9]+)*)\b",
        text
    )

    if match:
        return match.group(1)

    return None

# =====================================
# 5. PROCESS ALL YEARLY SHEETS
# =====================================

all_years = []
quality_reports = []

for sheet in yearly_sheets:

    year = int(sheet[-4:])

    print(f"\nProcessing {year}...")

    # Read the actual Excel header
    raw = pd.read_excel(
        workbook,
        sheet_name=sheet,
        header=0
    )

    # Identify station columns
    station_columns = {}

    for column in raw.columns[1:]:

        station_id = extract_station_id(column)

        if station_id is not None:
            station_columns[column] = station_id
        elif raw[column].notna().any():
            raise ValueError(
                f"Unrecognized column in {sheet}: "
                f"{column!r}"
            )

    if not station_columns:
        raise ValueError(
            f"No stations detected in {sheet}"
        )

    if len(set(station_columns.values())) != len(
        station_columns
    ):
        raise ValueError(
            f"Duplicate station IDs in {sheet}"
        )

    # First column contains timestamps
    timestamp_col = raw.columns[0]

    raw = raw.rename(
        columns={timestamp_col: "timestamp"}
    )

    # Excel already stores many dates as datetimes
    raw["timestamp"] = pd.to_datetime(
        raw["timestamp"],
        errors="coerce"
    )

    # Keep valid timestamps for the correct year
    raw = raw[
        raw["timestamp"].notna()
        & (raw["timestamp"].dt.year == year)
    ].copy()

    # Keep only timestamp and station columns
    raw = raw[
        ["timestamp"] + list(station_columns)
    ]

    raw = raw.rename(columns=station_columns)

    # Convert wide data to long data
    long_df = raw.melt(
        id_vars="timestamp",
        var_name="station_id",
        value_name="bicycle_count"
    )

    # Convert measurements into numeric values
    original_values = long_df["bicycle_count"].copy()

    long_df["bicycle_count"] = pd.to_numeric(
        original_values,
        errors="coerce"
    )

    invalid_text = (
        original_values.notna()
        & long_df["bicycle_count"].isna()
    ).sum()

    missing_count = (
        long_df["bicycle_count"].isna().sum()
    )

    negative_count = (
        long_df["bicycle_count"] < 0
    ).sum()

    non_integer_count = (
        (long_df["bicycle_count"].dropna() % 1) != 0
    ).sum()

    # Keep missing values for later coverage analysis
    # but reject invalid numeric measurements
    if negative_count or non_integer_count:
        raise ValueError(
            f"Invalid numeric counts in {sheet}: "
            f"{negative_count} negative, "
            f"{non_integer_count} non-integer"
        )

    if invalid_text:
        print(
            f"WARNING: {invalid_text} nonnumeric "
            "entries converted to missing"
        )

    long_df["year"] = year

    # Save annual quality information
    quality_reports.append({
        "year": year,
        "stations": len(station_columns),
        "observations": len(long_df),
        "missing_counts": missing_count,
        "negative_counts": negative_count,
        "invalid_text": invalid_text
    })

    print("Stations:", len(station_columns))
    print("Rows:", len(long_df))
    print("Missing measurements:", missing_count)

    all_years.append(long_df)

# =====================================
# 6. COMBINE ALL YEARS
# =====================================

combined = pd.concat(
    all_years,
    ignore_index=True
)

combined = combined.sort_values(
    ["station_id", "timestamp"],
    kind="stable"
).reset_index(drop=True)

# =====================================
# 7. DATA QUALITY CHECKS
# =====================================

duplicates = combined.duplicated(
    subset=["station_id", "timestamp"]
).sum()

print("\nDuplicate station-hour records:", duplicates)

# Report stations missing from location metadata
known_stations = set(stations["station_id"])

unknown_stations = (
    set(combined["station_id"]) - known_stations
)

print(
    "Stations without metadata:",
    sorted(unknown_stations)
)

# =====================================
# 8. SAVE PROCESSED DATA
# =====================================

combined.to_parquet(
    OUTPUT_DIR / "berlin_traffic_all_years.parquet",
    index=False
)

quality_df = pd.DataFrame(quality_reports)

quality_df.to_csv(
    OUTPUT_DIR / "data_quality_report.csv",
    index=False
)

# =====================================
# 9. FINAL SUMMARY
# =====================================

print("\n========== FINAL SUMMARY ==========")

print("Total rows:", len(combined))

print(
    "Unique stations:",
    combined["station_id"].nunique()
)

print(
    "Years:",
    sorted(combined["year"].unique())
)

print(
    "Date range:",
    combined["timestamp"].min(),
    "to",
    combined["timestamp"].max()
)

print("\nData quality by year:")
print(quality_df.to_string(index=False))

print("\nFiles saved successfully!")
