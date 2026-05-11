import pandas as pd

# LOAD Bronze data
df = pd.read_json("data/bronze/aapl_stock.json")

# SHOW original data
print("Original Data:")
print(df)

# KEEP only important columns
df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]

# CONVERT Date column
df["Date"] = pd.to_datetime(df["Date"])

# REMOVE missing values
df = df.dropna()

# SAVE cleaned data into Silver layer
df.to_json(
    "data/silver/aapl_cleaned.json",
    orient="records",
    indent=4,
    date_format="iso"
)

print("\nCleaned data saved to Silver layer!")