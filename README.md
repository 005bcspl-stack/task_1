OHLC Moving Average Analysis using Zerodha Kite

This project is a simple Python-based tool to fetch historical OHLC (Open, High, Low, Close) data and calculate Moving Averages. The processed data is exported into Excel files for easy analysis and tracking.

It’s mainly built for learning and experimenting with market data using the Zerodha Kite API.

Project Structure

ohlc_ma.py
Main script that fetches OHLC data and calculates moving averages.

keys.py
Contains API credentials required to connect to Zerodha Kite. This file should remain private.

Excel Output Files

kite_ohlc_ma.xlsx – General OHLC + MA output

kite_ohlc_ma_ADANIENT.xlsx – Sample output for ADANIENT

ohlc_with_ma.xlsx – Processed OHLC data with moving averages

__pycache__/
Automatically created by Python. Not needed for the project logic.

What This Project Does

Connects to Zerodha Kite API

Downloads historical OHLC data

Calculates moving averages (like MA20, MA50, etc.)

Saves the results into Excel files

Helps in basic technical analysis

Moving Average Calculation

Moving Average is calculated using closing prices over a defined number of periods.

Example for 20-period MA:

df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()


If fewer than 20 data points are available, it averages whatever data exists up to that point.

How to Run
1. Install Required Libraries
pip install pandas kiteconnect openpyxl

2. Add API Credentials

Edit keys.py and add your Zerodha API details:

api_key = "your_api_key"
api_secret = "your_api_secret"
access_token = "your_access_token"


Never share this file publicly.

3. Run the Script
python ohlc_ma.py


After running, Excel files containing OHLC and Moving Average data will be generated.

Output

The Excel sheet includes columns like:

Date | Open | High | Low | Close | MA20 | MA50

This makes it easy to analyze trends and price behavior.

Important Note

Add this to your .gitignore file to avoid uploading sensitive or unnecessary files:

keys.py
__pycache__/

Possible Improvements

Add more indicators (EMA, RSI, MACD)

Add chart visualization

Support multiple symbols at once

Automate daily data updates
