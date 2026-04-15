from functools import lru_cache
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.io as pio
from plotly.offline import get_plotlyjs
from flask import Flask, jsonify, render_template


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.data_analysis import generate_charts
from src.data_cleaning import (
    CLEANED_DATA_PATH,
    RAW_DATA_PATH,
    clean_data,
    load_raw_data,
    save_clean_data,
)
from src.database import DATABASE_PATH, store_data


app = Flask(__name__)
NUMERIC_COLUMNS = [
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]


def ensure_project_assets() -> None:
    if not CLEANED_DATA_PATH.exists():
        cleaned_df = clean_data(load_raw_data(RAW_DATA_PATH))
        save_clean_data(cleaned_df, CLEANED_DATA_PATH)

    df = pd.read_csv(CLEANED_DATA_PATH, parse_dates=["datetime"])
    generate_charts(df)
    store_data(df, DATABASE_PATH)


@lru_cache(maxsize=1)
def load_dataset() -> pd.DataFrame:
    ensure_project_assets()

    df = pd.read_csv(CLEANED_DATA_PATH, parse_dates=["datetime"])
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["datetime", "Global_active_power"]).copy()
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    df["month"] = df["datetime"].dt.to_period("M").astype(str)
    df["estimated_kwh"] = df["Global_active_power"] / 60.0
    return df


def _chart_html(figure, *, title: str) -> str:
    figure.update_layout(
        title=title,
        paper_bgcolor="#f6f4ed",
        plot_bgcolor="#f6f4ed",
        font={"family": "Georgia, serif", "color": "#111827"},
        height=360,
        margin={"l": 36, "r": 24, "t": 64, "b": 36},
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(gridcolor="#d6d3d1", zeroline=False)
    return pio.to_html(
        figure,
        full_html=False,
        include_plotlyjs=False,
        config={"displayModeBar": False, "responsive": True},
    )


@lru_cache(maxsize=1)
def build_dashboard_context() -> dict:
    df = load_dataset()

    hourly_avg = (
        df.groupby("hour", as_index=False)["Global_active_power"]
        .mean()
        .rename(columns={"Global_active_power": "avg_power"})
    )
    daily_energy = (
        df.groupby("date", as_index=False)["estimated_kwh"]
        .sum()
        .rename(columns={"estimated_kwh": "daily_kwh"})
    )
    monthly_avg = (
        df.groupby("month", as_index=False)["Global_active_power"]
        .mean()
        .rename(columns={"Global_active_power": "avg_power"})
    )
    submeter_totals = pd.DataFrame(
        {
            "meter": ["Sub Metering 1", "Sub Metering 2", "Sub Metering 3"],
            "value": [
                df["Sub_metering_1"].sum(),
                df["Sub_metering_2"].sum(),
                df["Sub_metering_3"].sum(),
            ],
        }
    )

    peak_hour_row = hourly_avg.sort_values("avg_power", ascending=False).iloc[0]
    highest_day = daily_energy.sort_values("daily_kwh", ascending=False).iloc[0]
    busiest_month = monthly_avg.sort_values("avg_power", ascending=False).iloc[0]
    summary = {
        "records": f"{len(df):,}",
        "date_range": f"{df['datetime'].min():%b %d, %Y} to {df['datetime'].max():%b %d, %Y}",
        "avg_power": round(df["Global_active_power"].mean(), 3),
        "peak_hour": f"{int(peak_hour_row['hour']):02d}:00",
        "peak_hour_usage": round(float(peak_hour_row["avg_power"]), 3),
        "daily_energy_avg": round(float(daily_energy["daily_kwh"].mean()), 1),
        "max_voltage": round(float(df["Voltage"].max()), 1),
        "min_voltage": round(float(df["Voltage"].min()), 1),
    }

    insights = [
        f"Peak demand concentrates around {summary['peak_hour']} with an average load of {summary['peak_hour_usage']} kW.",
        f"The heaviest day in the dataset reached {highest_day['daily_kwh']:.1f} kWh on {highest_day['date']:%b %d, %Y}.",
        f"{busiest_month['month']} is the strongest month on average at {busiest_month['avg_power']:.2f} kW.",
    ]

    hourly_fig = px.bar(
        hourly_avg,
        x="hour",
        y="avg_power",
        color="avg_power",
        color_continuous_scale=["#f59e0b", "#0f766e"],
        labels={"hour": "Hour of Day", "avg_power": "Average Power (kW)"},
    )
    hourly_fig.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside",
        hovertemplate="Hour %{x}:00<br>Average %{y:.2f} kW<extra></extra>",
    )
    daily_fig = px.line(
        daily_energy,
        x="date",
        y="daily_kwh",
        labels={"date": "Date", "daily_kwh": "Estimated Daily Energy (kWh)"},
    )
    daily_fig.update_traces(
        line={"color": "#1d4ed8", "width": 2},
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.1f} kWh<extra></extra>",
    )
    daily_fig.update_layout(hovermode="x unified")
    monthly_fig = px.area(
        monthly_avg,
        x="month",
        y="avg_power",
        labels={"month": "Month", "avg_power": "Average Power (kW)"},
    )
    monthly_fig.update_traces(
        line={"color": "#b45309", "width": 2},
        fillcolor="rgba(180, 83, 9, 0.25)",
        hovertemplate="%{x}<br>%{y:.2f} kW<extra></extra>",
    )
    submeter_fig = px.pie(
        submeter_totals,
        names="meter",
        values="value",
        color="meter",
        color_discrete_sequence=["#0f766e", "#1d4ed8", "#f59e0b"],
        hole=0.55,
    )
    submeter_fig.update_traces(
        textinfo="label+percent",
        hovertemplate="%{label}<br>%{value:.0f} total units<br>%{percent}<extra></extra>",
    )

    return {
        "summary": summary,
        "insights": insights,
        "plotly_js": get_plotlyjs(),
        "hourly_chart": _chart_html(hourly_fig, title="Average Demand by Hour"),
        "daily_chart": _chart_html(daily_fig, title="Daily Energy Pattern"),
        "monthly_chart": _chart_html(monthly_fig, title="Monthly Demand Shape"),
        "submeter_chart": _chart_html(submeter_fig, title="Sub-Metering Share"),
    }


@app.route("/")
def home():
    return render_template("dashboard.html", **build_dashboard_context())


@app.route("/summary")
def summary():
    return jsonify(build_dashboard_context()["summary"])


@app.route("/health")
def health():
    return jsonify({"status": "ok", "data_file": str(CLEANED_DATA_PATH.exists())})


if __name__ == "__main__":
    app.run(debug=True)
