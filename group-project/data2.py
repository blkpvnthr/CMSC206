# Load Libraries
import os
import datetime as dt
import random as rnd
from sys import float_info as sflt

from tqdm import tqdm
import numpy as np
import pandas as pd
import mplfinance as mpf
import pandas_ta as ta
import asyncio
import websockets
import json
import requests
import yfinance as yf

pd.set_option("max_rows", 100)
pd.set_option("max_columns", 20)

print(f"Numpy v{np.__version__}")
print(f"Pandas v{pd.__version__}")
print(f"mplfinance v{mpf.__version__}")
print(f"\nPandas TA v{ta.version}\nTo install the Latest Version:\n$ pip install -U git+https://github.com/twopirllc/pandas-ta\n")


# Google Sheets CSV Export Link (Replace FILE_ID with your actual Google Sheets ID)
google_sheets_csv_url = "https://docs.google.com/spreadsheets/d/178otvH3EwuKdDMrFDU3vY1-unFuw_jEcnIwjRybW2c4/export?format=csv"

# Load stock tickers from Google Sheets
df = pd.read_csv(google_sheets_csv_url)

# Ensure 'Ticker' column exists
if 'Ticker' not in df.columns:
    raise ValueError("Google Sheet must contain a 'Ticker' column.")

# Extract tickers
tickers = df["Ticker"].tolist()

# Function to fetch historical stock prices from Yahoo Finance
def get_historical_prices(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist[["Open", "High", "Low", "Close", "Volume"]]

# Fetch historical prices for all tickers
historical_data = {ticker: get_historical_prices(ticker) for ticker in tickers}
historical_df = pd.concat(historical_data, axis=1)

# Save historical data
historical_df.to_csv("historical_stock_prices.csv")
print("Historical Stock Prices Saved to CSV:")
print(historical_df.tail())

# Define Trend Analysis
def analyze_trend(asset):
    asset.ta.ema(length=8, append=True)
    asset.ta.ema(length=21, append=True)
    asset.ta.ema(length=50, append=True)
    asset.ta.percent_return(append=True)

    # Define Long Trend: EMA(8) > EMA(21)
    long = ta.ema(asset['Close'], 8) > ta.ema(asset['Close'], 21)

    print("TA Columns Added:")
    print(asset.tail())
    return long

# Perform trend analysis for the first stock
ticker = tickers[0]
asset = historical_data[ticker]
long_trend = analyze_trend(asset)

# Visualization
extime = ta.get_time(to_string=True)
first_date, last_date = asset.index[0], asset.index[-1]
f_date = f"{first_date.day_name()} {first_date.month}-{first_date.day}-{first_date.year}"
l_date = f"{last_date.day_name()} {last_date.month}-{last_date.day}-{last_date.year}"
last_ohlcv = f"Last OHLCV: ({asset.iloc[-1].Open:.4f}, {asset.iloc[-1].High:.4f}, {asset.iloc[-1].Low:.4f}, {asset.iloc[-1].Close:.4f}, {int(asset.iloc[-1].Volume)})"
ptitle = f"\n{ticker} [Daily for 1y] from {f_date} to {l_date}\n{last_ohlcv}\n{extime}"

# Plot Stock Prices with Trends
mpf.plot(asset, type="candle", volume=True, title=ptitle)

# Alpaca API credentials (Replace with your own)
ALPACA_API_KEY = "YOUR_ALPACA_API_KEY"
ALPACA_SECRET_KEY = "YOUR_ALPACA_SECRET_KEY"
ALPACA_FEED = "iex"  # Change to "sip" for paid plan
ALPACA_WS_URL = f"wss://stream.data.alpaca.markets/v2/{ALPACA_FEED}"

# Function to fetch live stock prices from Alpaca Markets API
async def alpaca_stream():
    async with websockets.connect(ALPACA_WS_URL) as ws:
        # Authenticate
        auth_data = {
            "action": "authenticate",
            "key_id": ALPACA_API_KEY,
            "secret_key": ALPACA_SECRET_KEY
        }
        await ws.send(json.dumps(auth_data))

        # Wait for authentication response
        response = await ws.recv()
        auth_response = json.loads(response)

        if auth_response.get("msg") != "authenticated":
            print("Authentication failed:", auth_response)
            return  # Stop execution if authentication fails

        print("✅ WebSocket authentication successful!")

        # Subscribe to stock updates
        subscription_data = {
            "action": "subscribe",
            "bars": tickers  # Subscribe to all tickers from the Google Sheet
        }
        await ws.send(json.dumps(subscription_data))

        # Read real-time data
        while True:
            data = await ws.recv()
            print("Live Data:", data)

# Run WebSocket connection
asyncio.run(alpaca_stream())
