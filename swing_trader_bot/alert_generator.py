"""
alert_generator.py
Purpose: Turn breakout signals into actionable trade picks
Location: swing_trader_bot/alert_generator.py
"""

import os
import pandas as pd
from datetime import datetime

SIGNALS_FILE = "data/trading_signals.csv"
PICKS_FILE = "data/daily_picks.csv"

RISK_PERCENT = 0.02  # 2% of portfolio per trade
WALLET_BALANCE = 10000  # pretend trading account

def generate_alerts():
    if not os.path.exists(SIGNALS_FILE):
        print("❌ No signals found. Run pattern_detector.py first.")
        return

    df = pd.read_csv(SIGNALS_FILE)

    alerts = []
    for _, row in df.iterrows():
        entry = row["Close"]
        stop = round(entry * 0.97, 2)        # 3% stop loss
        target = round(entry * 1.08, 2)      # 8% target gain
        risk_amount = WALLET_BALANCE * RISK_PERCENT
        confidence = row.get("Confidence", "Medium")

        alert = {
            "Date": row["Date"],
            "Ticker": row["Ticker"],
            "Strategy": row["Signal"],
            "Entry": round(entry, 2),
            "Stop": stop,
            "Target": target,
            "Risk": f"${risk_amount:.0f}",
            "Confidence": confidence,
            "Reasoning": "Breakout above 20-day high with volume spike"
        }
        alerts.append(alert)

    if alerts:
        pd.DataFrame(alerts).to_csv(PICKS_FILE, index=False)

        # Telegram-style formatting starts here
        print("\n📣 TRADE ALERTS FOR TODAY:\n")
        for alert in alerts:
            message = f"""🚨 TRADE ALERT: ${alert['Ticker']}
📈 Strategy: {alert['Strategy']}
📍 Entry: ${alert['Entry']}
📉 Stop: ${alert['Stop']}
🎯 Target: ${alert['Target']}
📊 Confidence: {alert['Confidence']}
💰 Risk: {alert['Risk']}
🧠 Reasoning: {alert['Reasoning']}"""
            print(message)
            print("-" * 40)
    else:
        print("🔍 No valid alerts generated.")

if __name__ == "__main__":
    generate_alerts()
