import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

# === Configuration ===
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 300))
TIMEZONE = timezone("Asia/Dhaka")

# === Setup ===
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, workers=4, use_context=True)
logging.basicConfig(level=logging.INFO)

# Strong 5 Currency Pairs (excluding BTC)
PAIRS = ["EUR/USD", "GBP/USD", "AUD/USD", "USD/JPY", "USD/CHF"]
interval_seconds = DEFAULT_INTERVAL
last_directions = {}

# === Trend Analysis ===
def get_trend(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=3&apikey={API_KEY}"
    try:
        res = requests.get(url).json()
        values = res.get("values", [])
        if len(values) < 3:
            raise ValueError("Not enough data")
        c1 = float(values[0]['close'])
        c2 = float(values[1]['close'])
        c3 = float(values[2]['close'])
        if c1 > c2 > c3:
            return 'UP'
        elif c1 < c2 < c3:
            return 'DOWN'
    except Exception as e:
        logging.error(f"Error fetching trend for {symbol}: {e}")
    return None

def generate_signal():
    signals = {}
    for symbol in PAIRS:
        trend = get_trend(symbol)
        if trend:
            signals[symbol] = trend
    return signals

def send_best_signal():
    global last_directions
    all_signals = generate_signal()

    if not all_signals:
        bot.send_message(chat_id=GROUP_ID, text="⚠️ No strong signal found in this round.")
        return

    best_pair = list(all_signals.keys())[0]
    direction = all_signals[best_pair]
    now = datetime.now(TIMEZONE).strftime('%I:%M %p')

    last_directions[now] = (best_pair, direction)

    msg = (
        "🚨 *Trade Signal Alert*

"
        f"💹 *Pair:* {best_pair}
"
        f"📊 *Direction:* {'📈' if direction == 'UP' else '📉'} {direction}
"
        f"🕒 *Time:* {now}
"
        "⏱ *Duration:* 1 Minute

"
        "⚠️ Place this trade manually on Quotex!"
    )
    bot.send_message(chat_id=GROUP_ID, text=msg, parse_mode='Markdown')

# === Commands ===
def start(update: Update, context):
    update.message.reply_text(
        "👋 Welcome to *Quotex Pro Signal Bot!*

"
        "I send high-accuracy signals every few minutes based on market trends.
"
        "Use /timeset <seconds> to change the signal interval.

"
        "✅ Example: `/timeset 180` to get signals every 3 minutes.",
        parse_mode='Markdown'
    )

def timeset(update: Update, context):
    global interval_seconds
    try:
        if context.args:
            new_time = int(context.args[0])
            interval_seconds = new_time
            update.message.reply_text(f"⏱ Signal interval updated to {interval_seconds} seconds.")
        else:
            raise ValueError
    except Exception:
        update.message.reply_text("❌ Invalid format. Use: /timeset 120")

# === Dispatcher Setup ===
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("timeset", timeset))

# === Flask Webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "Quotex Pro Signal Bot is Live!", 200

# === Signal Threading ===
def run_scheduler():
    while True:
        send_best_signal()
        threading.Event().wait(interval_seconds)

threading.Thread(target=run_scheduler, daemon=True).start()

# === Run App ===
if __name__ == "__main__":
    logging.info("Starting Quotex Pro Signal Bot...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
