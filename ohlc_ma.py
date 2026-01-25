from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import pandas as pd


from keys import api_k, access_token


# Connect to Zerodha
kite = KiteConnect(api_key=api_k)
kite.set_access_token(access_token)
print("Connected to Zerodha")


# User inputs
symbol = input("Enter stock symbol (example: RELIANCE): ").strip().upper()
days = int(input("Enter number of days: "))
exchange = "NSE"


# Find instrument token
instrument_token = None
for inst in kite.instruments(exchange):
    if inst["tradingsymbol"] == symbol:
        instrument_token = inst["instrument_token"]
        break

if instrument_token is None:
    print("Invalid symbol")
    exit()

print("Instrument token:", instrument_token)


# Date range
to_date = datetime.now().date()
from_date = to_date - timedelta(days=days)


# Fetch historical data
data = kite.historical_data(
    instrument_token,
    from_date,
    to_date,
    interval="day"
)

if not data:
    print("No data received")
    exit()


# Convert to DataFrame
df = pd.DataFrame(data)


# Moving averages
df["MA20"] = df["close"].rolling(20, min_periods=1).mean().round(2)
df["MA200"] = df["close"].rolling(200, min_periods=1).mean().round(2)


# Rename columns for clarity
df.rename(columns={
    "date": "DATE",
    "open": "OPEN",
    "high": "HIGH",
    "low": "LOW",
    "close": "CLOSE",
    "volume": "VOLUME"
}, inplace=True)

df["DATE"] = df["DATE"].astype(str)


# Quick preview
print(df[["DATE", "CLOSE", "MA20", "MA200"]].tail())


# Save to Excel
output_file = f"kite_ohlc_ma_{symbol}.xlsx"
df.to_excel(output_file, index=False)
print("Excel file saved:", output_file)