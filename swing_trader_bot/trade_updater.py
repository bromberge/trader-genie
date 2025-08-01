"""
trade_updater.py
Purpose: Check open trades using real price data (via yfinance),
update win/loss status, and track wallet balance.
"""

import os
import pandas as pd
import yfinance as yf

RESULTS_FILE = "data/results_tracking.csv"
MAX_HOLD_DAYS = 5
STARTING_BALANCE = 10000
RISK_PER_TRADE = 0.02  # 2% per trade

def get_latest_price(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1d", progress=False)
        if not df.empty:
            return round(df['Close'].iloc[-1], 2)
    except Exception as e:
        print(f"⚠️ Failed to fetch price for {ticker}: {e}")
    return None

def update_trades():
    if not os.path.exists(RESULTS_FILE):
        print("❌ No results file found. Run trade_logger.py first.")
        return

    df = pd.read_csv(RESULTS_FILE)

    updated = []
    balance = STARTING_BALANCE

    for idx, row in df.iterrows():
        # Carry forward last known wallet balance
        if idx > 0 and pd.notna(updated[-1]["Wallet_After"]):
            balance = updated[-1]["Wallet_After"]

        if row["Status"] == "CLOSED":
            # Just keep existing row and balance
            if pd.isna(row["Wallet_After"]):
                row["Wallet_After"] = balance
            updated.append(row)
            continue

        # Trade is still open — update it
        days_held = row["Days_Held"] + 1
        current_price = get_latest_price(row["Ticker"])

        if current_price is None:
            row["Days_Held"] = days_held
            updated.append(row)
            continue

        # Check outcome
        if current_price >= row["Target"]:
            row["Status"] = "CLOSED"
            row["Result"] = "WIN"
            pnl = (row["Target"] - row["Executed_Price"]) * get_share_size(balance)
            balance += pnl
        elif current_price <= row["Stop"]:
            row["Status"] = "CLOSED"
            row["Result"] = "LOSS"
            pnl = (row["Stop"] - row["Executed_Price"]) * get_share_size(balance)
            balance += pnl
        elif days_held >= MAX_HOLD_DAYS:
            row["Status"] = "CLOSED"
            row["Result"] = "TIMEOUT"
            pnl = 0  # flat close
        else:
            pnl = 0  # trade is still open

        row["Days_Held"] = days_held
        row["Wallet_After"] = round(balance, 2)
        updated.append(row)

    updated_df = pd.DataFrame(updated)
    updated_df.to_csv(RESULTS_FILE, index=False)
    print(f"✅ Trades updated using real prices. Wallet now: ${round(balance, 2)}")

def get_share_size(wallet_balance):
    """Simulate fixed % risk with per-trade capital use"""
    return round(wallet_balance * RISK_PER_TRADE / 100, 2)  # Simplified: 1% risk = ~$1/share

if __name__ == "__main__":
    update_trades()
