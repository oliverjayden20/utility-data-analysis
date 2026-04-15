Utility Data Analysis & Optimization Tool

Overview

This project analyzes global electricity consumption data to identify usage patterns, peak demand periods, and potential optimization opportunities.

Technologies Used
    Python (Pandas, Matplotlib)
    SQL (SQLite)
    Flask (Web Application)

Features
    Data cleaning and preprocessing pipeline
    Time-based energy usage analysis
    SQL database integration for querying
    Basic web interface to display usage summaries

Key Insights
    Identified peak electricity usage hours
    Analyzed daily consumption trends
    Calculated average and total energy usage

How to Run

Install dependencies:

pip install -r requirements.txt

Run data pipeline:

python src/data_cleaning.py
python src/data_analysis.py
python src/database.py

Run app:

python app/app.py