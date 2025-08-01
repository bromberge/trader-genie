"""
telegram_sender.py
Purpose: Sends daily trade picks to Telegram
"""

import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PICKS_FILE = "data/daily_picks.csv"

def format_message(alert):
    return f"""🚨 TRADE ALERT: ${alert['Ticker']}
📈 Strategy: {alert['Strategy']}
📍 Entry: ${alert['Entry']}
📉 Stop: ${alert['Stop']}
🎯 Target: ${alert['Target']}
📊 Confidence: {alert['Confidence']}
💰 Risk: {alert['Risk']}
🧠 Reasoning: {alert['Reasoning']}"""

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Message sent to Telegram")
    else:
        print("❌ Failed to send message")
        print(response.text)

def main():
    if not os.path.exists(PICKS_FILE):
        print("❌ daily_picks.csv not found.")
        return

    df = pd.read_csv(PICKS_FILE)
    for _, row in df.iterrows():
        message = format_message(row)
        send_to_telegram(message)

if __name__ == "__main__":
    main()
