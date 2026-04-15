import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/cleaned_data.csv")

df['datetime'] = pd.to_datetime(df['datetime'])

df['hour'] = df['datetime'].dt.hour

peak_usage = df.groupby('hour')['Global_active_power'].mean()

peak_usage.plot()
plt.title("Average Usage by Hour")
plt.xlabel("Hour")
plt.ylabel("Power Consumption")

plt.savefig("outputs/charts/peak_usage.png")
plt.close()

print("Analysis complete. Chart saved.")