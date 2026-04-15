import sqlite3
from pathlib import Path
import sys

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data_cleaning import CLEANED_DATA_PATH

DATABASE_PATH = BASE_DIR / "data" / "utility.db"


def load_clean_data(path: Path = CLEANED_DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["datetime"])


def store_data(df: pd.DataFrame, db_path: Path = DATABASE_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        df.to_sql("usage_data", connection, if_exists="replace", index=False)

    return db_path


def get_top_peak_hours(db_path: Path = DATABASE_PATH) -> pd.DataFrame:
    query = """
        SELECT
            strftime('%H', datetime) AS hour,
            ROUND(AVG(Global_active_power), 3) AS avg_usage
        FROM usage_data
        GROUP BY hour
        ORDER BY avg_usage DESC
        LIMIT 5
    """

    with sqlite3.connect(db_path) as connection:
        return pd.read_sql_query(query, connection)


def main() -> None:
    df = load_clean_data()
    store_data(df)
    top_hours = get_top_peak_hours()
    print(f"Stored dataset in {DATABASE_PATH}")
    print("Top 5 peak usage hours:")
    print(top_hours.to_string(index=False))


if __name__ == "__main__":
    main()
