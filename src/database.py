import pandas as pd
import sqlite3

df = pd.read_csv("data/cleaned_data.csv")

conn = sqlite3.connect("data/utility.db")

df.to_sql("usage_data", conn, if_exists="replace", index=False)

print("Data stored in database.")

query = """
SELECT strftime('%H', datetime) AS hour, AVG(Global_active_power) as avg_usage
FROM usage_data
GROUP BY hour
ORDER BY avg_usage DESC
LIMIT 5;
"""

result = pd.read_sql_query(query, conn)

result.index = result.index + 1

print("Top 5 peak usage hours:")
print(result)

conn.close()