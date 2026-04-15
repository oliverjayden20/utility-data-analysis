from pathlib import Path
import sys

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data_cleaning import CLEANED_DATA_PATH


matplotlib.use("Agg")

OUTPUTS_DIR = BASE_DIR / "outputs" / "charts"


def load_clean_data(path: Path = CLEANED_DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["datetime"])


def generate_charts(df: pd.DataFrame, output_dir: Path = OUTPUTS_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    hourly_usage = df.groupby(df["datetime"].dt.hour)["Global_active_power"].mean()
    daily_usage = (
        df.set_index("datetime")["Global_active_power"].resample("D").mean().dropna()
    )
    monthly_usage = (
        df.set_index("datetime")["Global_active_power"].resample("ME").mean().dropna()
    )

    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 5))
    hourly_usage.plot(ax=ax, color="#0f766e", linewidth=2.5)
    ax.set_title("Average Power Usage by Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Global Active Power (kW)")
    fig.tight_layout()
    fig.savefig(output_dir / "peak_usage.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    daily_usage.plot(ax=ax, color="#1d4ed8", linewidth=1.5)
    ax.set_title("Daily Average Power Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Global Active Power (kW)")
    fig.tight_layout()
    fig.savefig(output_dir / "daily_usage.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    monthly_usage.plot(ax=ax, color="#b45309", linewidth=2.5)
    ax.set_title("Monthly Average Power Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Global Active Power (kW)")
    fig.tight_layout()
    fig.savefig(output_dir / "monthly_usage.png", dpi=200)
    plt.close(fig)


def main() -> None:
    df = load_clean_data()
    generate_charts(df)
    print(f"Saved charts to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
