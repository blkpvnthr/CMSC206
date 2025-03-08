# Author: Asmaa Abdul-Amin
# CRN#: 32016
# This script imports a list of Defense Stocks from a CSV file that can be used to fetch the latest stock prices using the TradingView API.
# The stock prices can then be displayed to the user and saved to a new CSV file with the updated data.

import os
import dotenv
import pandas as pd
import yfinance as yf
import asyncio
import websockets
import json
import matplotlib.pyplot as plt
import mplfinance as mpf


# Load API keys from .env
dotenv.load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Ensure API keys are set
if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise ValueError("Missing Alpaca API credentials in .env file!")

# Google Drive CSV Direct Link (Replace with your actual link)
google_drive_csv_url = "https://drive.google.com/uc?id=1_09iFs0UXSXsCOPHFC1H67xQpjdpc1TL"

# Load stock symbols from CSV
df = pd.read_csv(google_drive_csv_url)

# Ensure 'Symbol' column exists
if 'Symbol' not in df.columns:
    raise ValueError("CSV file must contain a 'Symbol' column.")

# Function to fetch historical stock prices from Yahoo Finance
def get_historical_prices(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y")  # Get last 1 year of data
    
    if hist.empty:
        print(f"⚠️ Warning: No data found for {symbol}. Stock might be delisted.")
        return None  # Return None for missing stocks
    
    return hist["Close"]

# Fetch historical prices for all symbols
historical_data = {}

for symbol in df["Symbol"]:
    try:
        data = get_historical_prices(symbol)
        if data is not None:
            historical_data[symbol] = data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

# Convert to DataFrame and save as CSV
historical_df = pd.DataFrame(historical_data)

# Ensure we have valid data before proceeding
if historical_df.empty:
    raise ValueError("No valid stock data found. Check if stocks are delisted or API issues.")

# Plot historical prices for top-performing stocks
plt.figure(figsize=(12, 6))

for ticker in historical_data:
    plt.plot(historical_data[ticker], label=ticker)
plt.title("Top Performing Stocks (Based on Returns)")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.legend()
plt.show()


# Function to calculate stock returns safely
def calculate_returns(historical_prices):
    if len(historical_prices) < 2:  # Ensure we have at least 2 data points
        return None
    return (historical_prices.iloc[-1] - historical_prices.iloc[0]) / historical_prices.iloc[0]

# Identify top-performing stocks based on returns
returns = {
    symbol: calculate_returns(historical_data[symbol])
    for symbol in historical_data if calculate_returns(historical_data[symbol]) is not None
}

# Ensure we have valid stocks with returns
if not returns:
    raise ValueError("No stocks with valid returns found.")

# Select top 5 performing stocks
top_stocks = sorted(returns, key=returns.get, reverse=True)[:5]

# Plot historical prices for top-performing stocks
plt.figure(figsize=(12, 6))

for symbol in top_stocks:
    plt.plot(historical_data[symbol], label=symbol)

plt.title("Top Performing Stocks (Based on Returns)")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.legend()
plt.show()




import os
import dotenv
import pandas as pd
import asyncio
import websockets
import json
from alpaca.data.live import StockDataStream
from datetime import datetime
import pytz

# Load Alpaca API keys
dotenv.load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Function to check if the market is open (based on datetime)
def is_market_open():
    # Define US Eastern Time Zone
    eastern = pytz.timezone("America/New_York")

    # Get current time in Eastern Time
    now = datetime.now(eastern)

    # Market is open Monday–Friday, 9:30 AM – 4:00 PM ET
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)

    if now.weekday() in range(0, 5) and market_open_time <= now <= market_close_time:
        print(f"✅ The market is open (Current time: {now.strftime('%Y-%m-%d %I:%M %p ET')}). Starting live data stream...")
        return True
    else:
        print(f"❌ The market is closed (Current time: {now.strftime('%Y-%m-%d %I:%M %p ET')}). Exiting program.")
        return False

# If market is closed, exit
if not is_market_open():
    exit()

# Initialize WebSocket Client for Live Data
wss_client = StockDataStream(ALPACA_API_KEY, ALPACA_SECRET_KEY)

# Async handler for live quote data
async def quote_data_handler(data):
    print(data)  # Print live market data

# Subscribe to SPY quotes
wss_client.subscribe_quotes(quote_data_handler, "SPY")

# Run WebSocket Client
wss_client.run()
