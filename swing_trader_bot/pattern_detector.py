"""
pattern_detector.py
Purpose: Detect simple breakout patterns from stock data
Location: swing_trader_bot/pattern_detector.py
"""

import pandas as pd
import os

DATA_DIR = "data"
PRICE_FILE = os.path.join(DATA_DIR, "stock_prices.csv")
SIGNALS_FILE = os.path.join(DATA_DIR, "trading_signals.csv")

def detect_breakouts(df, window=20):
    """Detect breakout patterns and return signal rows"""
    signals = []

    for ticker in df['Ticker'].unique():
        stock_df = df[df['Ticker'] == ticker].sort_values('Date')

        if len(stock_df) < window + 1:
            continue  # not enough history

        # Separate yesterday from the previous window
        recent = stock_df.iloc[-(window+1):-1]
        latest = stock_df.iloc[-1]

        highest_close = recent['Close'].max()
        avg_volume = recent['Volume'].mean()

        breakout = (
            latest['Close'] > highest_close and
            latest['Volume'] >= 2 * avg_volume
        )

        if breakout:
            signals.append({
                "Date": latest['Date'],
                "Ticker": ticker,
                "Signal": "Breakout",
                "Confidence": "High",
                "Close": latest['Close'],
                "Volume": latest['Volume']
            })

    return pd.DataFrame(signals)

def run_pattern_detection():
    if not os.path.exists(PRICE_FILE):
        print("❌ stock_prices.csv not found. Run data_collector.py first.")
        return

    df = pd.read_csv(PRICE_FILE)
    signal_df = detect_breakouts(df)

    if not signal_df.empty:
        signal_df.to_csv(SIGNALS_FILE, index=False)
        print(f"✅ {len(signal_df)} breakout signals saved to {SIGNALS_FILE}")
    else:
        print("🔍 No breakout patterns found today.")

if __name__ == "__main__":
    run_pattern_detection()
