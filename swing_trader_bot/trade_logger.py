"""
trade_logger.py
Purpose: Simulate trade entries and log them with fake execution
"""

import os
import pandas as pd
from datetime import datetime
import random

DAILY_PICKS_FILE = "data/daily_picks.csv"
RESULTS_FILE = "data/results_tracking.csv"

SIMULATED_DELAY_MINUTES = 5
STARTING_BALANCE = 10000

def simulate_entry(entry_price):
    """Simulate price movement after 5 minutes"""
    # Random small movement around entry (±0.5%)
    fluctuation = entry_price * random.uniform(-0.005, 0.005)
    return round(entry_price + fluctuation, 2)

def log_trades():
    if not os.path.exists(DAILY_PICKS_FILE):
        print("❌ No daily picks to log. Run alert_generator.py first.")
        return

    picks_df = pd.read_csv(DAILY_PICKS_FILE)

    logs = []
    for _, row in picks_df.iterrows():
        executed_price = simulate_entry(row['Entry'])

        log = {
            "Date": row["Date"],
            "Ticker": row["Ticker"],
            "Strategy": row["Strategy"],
            "Entry_Price": row["Entry"],
            "Executed_Price": executed_price,
            "Stop": row["Stop"],
            "Target": row["Target"],
            "Confidence": row["Confidence"],
            "Status": "OPEN",
            "Result": None,
            "Days_Held": 0,
            "Wallet_Before": STARTING_BALANCE,
            "Wallet_After": None
        }
        logs.append(log)

    new_logs = pd.DataFrame(logs)

    try:
        if os.path.getsize(RESULTS_FILE) > 0:
            existing = pd.read_csv(RESULTS_FILE)
            all_logs = pd.concat([existing, new_logs], ignore_index=True)
        else:
            all_logs = new_logs
    except FileNotFoundError:
        all_logs = new_logs

    all_logs.to_csv(RESULTS_FILE, index=False)
    print(f"✅ {len(logs)} new trades logged to {RESULTS_FILE}")


if __name__ == "__main__":
    log_trades()
