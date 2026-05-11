import pandas as pd

# LOAD Silver data
df = pd.read_json("data/silver/aapl_cleaned.json")

# CREATE analytics
analytics = {
    "average_close": df["Close"].mean(),
    "highest_price": df["High"].max(),
    "lowest_price": df["Low"].min(),
    "total_volume": int(df["Volume"].sum())
}

# CONVERT to DataFrame
analytics_df = pd.DataFrame([analytics])

# SAVE into Gold layer
analytics_df.to_json(
    "data/gold/aapl_analytics.json",
    orient="records",
    indent=4
)

print("Gold analytics saved successfully!")