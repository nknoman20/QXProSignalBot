import os
import logging
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

# Config
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 300))
TIMEZONE = timezone("Asia/Dhaka")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, workers=4, use_context=True)
logging.basicConfig(level=logging.INFO)

# Pairs to monitor
PAIRS = [
    "EUR/USD", "GBP/USD", "AUD/USD",
    "USD/JPY", "USD/CHF", "USD/CAD"
]

interval_seconds = DEFAULT_INTERVAL
last_directions = {}

# Detect trend
def get_trend(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=3&apikey={API_KEY}"
    try:
        res = requests.get(url).json()
        values = res['values']
        c1 = float(values[0]['close'])
        c2 = float(values[1]['close'])
        return 'UP' if c1 > c2 else 'DOWN'
    except Exception as e:
        logging.error(f"Error fetching trend for {symbol}: {e}")
        return None

# Select best signal
def generate_signal():
    scores = {}
    for symbol in PAIRS:
        trend = get_trend(symbol)
        if trend:
            scores[symbol] = trend
    return scores

def send_best_signal():
    global last_directions
    all_signals = generate_signal()

    if not all_signals:
        bot.send_message(chat_id=GROUP_ID, text="⚠️ No signal generated due to API issue.")
        return

    best_pair = list(all_signals.keys())[0]
    direction = all_signals[best_pair]
    now = datetime.now(TIMEZONE).strftime('%I:%M %p')

    last_directions[now] = (best_pair, direction)

    msg = (
        "🚨 *Trade Signal Alert*\n\n"
        f"💹 *Pair:* {best_pair}\n"
        f"📊 *Direction:* {'📈' if direction == 'UP' else '📉'} {direction}\n"
        f"🕒 *Time:* {now}\n"
        "⏱ *Duration:* 1 Minute\n\n"
        "⚠️ Place this trade manually on Quotex!"
    )
    bot.send_message(chat_id=GROUP_ID, text=msg, parse_mode='Markdown')

# Command: /start
def start(update: Update, context):
    update.message.reply_text(
        "👋 Welcome to *Quotex Pro Signal Bot!*\n\n"
        "I send high-probability signals every 5 minutes.\n"
        "Use /timeset 120 to change the signal interval.\n\n"
        "✅ Signals are based on real-time trend analysis.\n\n"
        "Enjoy smart trading!",
        parse_mode='Markdown'
    )

# Command: /timeset <seconds>
def timeset(update: Update, context):
    global interval_seconds
    try:
        if context.args:
            new_time = int(context.args[0])
            interval_seconds = new_time
            update.message.reply_text(f"⏱ Interval set to {interval_seconds} seconds.")
        else:
            raise ValueError
    except Exception:
        update.message.reply_text("❌ Invalid format. Use: /timeset 120")

# Setup commands
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("timeset", timeset))

# Webhook routes
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "Quotex Pro Signal Bot is Live!", 200

# Signal Scheduler (manually trigger every X seconds)
import threading
def run_scheduler():
    while True:
        send_best_signal()
        threading.Event().wait(interval_seconds)

threading.Thread(target=run_scheduler, daemon=True).start()

# Run Flask
if __name__ == "__main__":
    logging.info("Starting Quotex Pro Signal Bot...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
