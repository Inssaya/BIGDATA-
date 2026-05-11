import yfinance as yf
import json

ticker = "AAPL"
stock = yf.Ticker(ticker)

data = stock.history(period="1d")

# convert DataFrame → JSON
records = data.reset_index().to_dict(orient="records")

# save into Bronze layer
with open("data/bronze/aapl_stock.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=4, default=str)

print("Saved to Bronze layer successfully!")