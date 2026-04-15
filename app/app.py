from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "cleaned_data.csv")

@app.route("/")
def home():
    return "Utility Data Project is running."

@app.route("/summary")
def summary():
    df = pd.read_csv(DATA_PATH)
    total_usage = df['Global_active_power'].sum()
    avg_usage = df['Global_active_power'].mean()
    return f"Total Usage: {total_usage} | Average Usage: {avg_usage}"

if __name__ == "__main__":
    app.run(debug=True)