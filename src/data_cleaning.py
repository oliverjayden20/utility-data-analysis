import pandas as pd

print("STARTING SCRIPT")

df = pd.read_csv("data/raw_data.csv")

print("COLUMNS:")
print(df.columns)

df = df.dropna()

df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)

df.to_csv("data/cleaned_data.csv", index=False)

print("DONE")