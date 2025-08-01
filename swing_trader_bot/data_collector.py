# TraderGenie / swing_trader_bot / data_collector.py
# Downloads stock prices from Alpha Vantage (with yfinance backup)

import os
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# List of tickers to fetch
TICKERS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN']
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "stock_prices.csv")

def fetch_alpha_vantage(ticker):
    """Try to get stock data from Alpha Vantage"""
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": ALPHA_VANTAGE_KEY,
        "outputsize": "compact"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            return None

        latest_date = sorted(time_series.keys())[-1]
        entry = time_series[latest_date]
        return {
            "Date": latest_date,
            "Ticker": ticker,
            "Open": float(entry["1. open"]),
            "High": float(entry["2. high"]),
            "Low": float(entry["3. low"]),
            "Close": float(entry["4. close"]),
            "Volume": int(entry["6. volume"])
        }
    except Exception as e:
        print(f"Alpha Vantage error for {ticker}: {e}")
        return None

def fetch_yfinance(ticker):
    """Fallback: get stock data from yfinance"""
    try:
        data = yf.download(ticker, period="2d", interval="1d")
        if data.empty:
            return None
        row = data.iloc[-1]
        return {
            "Date": row.name.strftime('%Y-%m-%d'),
            "Ticker": ticker,
            "Open": row['Open'],
            "High": row['High'],
            "Low": row['Low'],
            "Close": row['Close'],
            "Volume": int(row['Volume'])
        }
    except Exception as e:
        print(f"yfinance error for {ticker}: {e}")
        return None

def fetch_and_save_prices(tickers):
    all_data = []

    for ticker in tickers:
        row = fetch_alpha_vantage(ticker)
        if row is None:
            print(f"⚠️ Falling back to yfinance for {ticker}")
            row = fetch_yfinance(ticker)
        if row:
            all_data.append(row)
        else:
            print(f"❌ Failed to fetch data for {ticker}")

    if all_data:
        df = pd.DataFrame(all_data)
        os.makedirs(DATA_DIR, exist_ok=True)
        df.to_csv(CSV_FILE, index=False)
        print(f"✅ Saved {len(df)} rows to {CSV_FILE}")
    else:
        print("⚠️ No data fetched.")

if __name__ == "__main__":
    fetch_and_save_prices(TICKERS)
