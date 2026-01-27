from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta
from key import api_k, access_token


# --------------------------------------------------
# 1. CONNECT TO ZERODHA
# --------------------------------------------------
kite = KiteConnect(api_key=api_k)
kite.set_access_token(access_token)
print("Connected to Zerodha")


# --------------------------------------------------
# 2. ASK USER FOR DAYS
# --------------------------------------------------
days = int(input("Enter number of days (max 60): "))


# --------------------------------------------------
# 3. FIND SENSEX TOKEN
# --------------------------------------------------
sensex_token = None

for inst in kite.instruments():
    name = str(inst.get("name", "")).upper()
    symbol = str(inst.get("tradingsymbol", "")).upper()

    if name == "SENSEX" or symbol == "SENSEX":
        sensex_token = inst["instrument_token"]
        break

if sensex_token is None:
    print("SENSEX not found")
    exit()

print("SENSEX token found:", sensex_token)


# --------------------------------------------------
# 4. SET DATE RANGE
# --------------------------------------------------
to_date = datetime.now()
from_date = to_date - timedelta(days=days)


# --------------------------------------------------
# 5. FETCH MINUTE DATA
# --------------------------------------------------
data = kite.historical_data(
    instrument_token=sensex_token,
    from_date=from_date,
    to_date=to_date,
    interval="minute"
)

if not data:
    print("No data received")
    exit()

df = pd.DataFrame(data)


# --------------------------------------------------
# 6. PREPARE FINAL TABLE
# --------------------------------------------------
final_df = pd.DataFrame()

final_df["DATE"] = pd.to_datetime(df["date"]).dt.strftime("%d-%m-%Y")
final_df["TIME"] = pd.to_datetime(df["date"]).dt.strftime("%H:%M")
final_df["PRICE"] = df["close"]

final_df["MA20"] = final_df["PRICE"].rolling(20, min_periods=1).mean().round(2)
final_df["MA200"] = final_df["PRICE"].rolling(200, min_periods=1).mean().round(2)


# --------------------------------------------------
# 7. SAVE TO EXCEL
# --------------------------------------------------
file_name = "sensex_date_time_ma.xlsx"
final_df.to_excel(file_name, index=False)

print("Excel saved:", file_name)
print(final_df.head())
