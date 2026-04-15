from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw_data.csv"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_data.csv"
NUMERIC_COLUMNS = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.replace("?", pd.NA).dropna().copy()

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna().copy()
    cleaned["datetime"] = pd.to_datetime(
        cleaned["Date"] + " " + cleaned["Time"],
        dayfirst=True,
    )

    return cleaned.sort_values("datetime").reset_index(drop=True)


def save_clean_data(df: pd.DataFrame, path: Path = CLEANED_DATA_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def run_cleaning() -> pd.DataFrame:
    raw_df = load_raw_data()
    cleaned_df = clean_data(raw_df)
    save_clean_data(cleaned_df)
    return cleaned_df


def main() -> None:
    cleaned_df = run_cleaning()
    print(f"Cleaned {len(cleaned_df):,} rows.")
    print(f"Saved cleaned dataset to {CLEANED_DATA_PATH}")


if __name__ == "__main__":
    main()
