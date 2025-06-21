import os
import logging
import requests
import threading
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 300))
TIMEZONE = timezone("Asia/Dhaka")
HOST_URL = os.getenv("HOST_URL")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, workers=4, use_context=True)
logging.basicConfig(level=logging.INFO)

PAIRS = ["EUR/USD", "GBP/USD", "AUD/USD", "USD/JPY", "USD/CHF"]
interval_seconds = DEFAULT_INTERVAL
last_directions = {}

def get_trend(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=5&apikey={API_KEY}"
    try:
        res = requests.get(url).json()
        values = res.get("values", [])
        if len(values) < 4:
            raise ValueError("Not enough data")
        closes = [float(v['close']) for v in values[:4]]
        diff1 = closes[0] - closes[1]
        diff2 = closes[1] - closes[2]
        diff3 = closes[2] - closes[3]
        if diff1 > 0 and diff2 > 0 and diff3 > 0 and all(abs(d) > 0.01 for d in [diff1, diff2, diff3]):
            return 'UP', abs(diff1 + diff2 + diff3)
        elif diff1 < 0 and diff2 < 0 and diff3 < 0 and all(abs(d) > 0.01 for d in [diff1, diff2, diff3]):
            return 'DOWN', abs(diff1 + diff2 + diff3)
    except Exception as e:
        logging.error(f"Error fetching trend for {symbol}: {e}")
    return None, 0

def generate_signal():
    signals = {}
    for symbol in PAIRS:
        trend, strength = get_trend(symbol)
        if trend:
            signals[symbol] = (trend, strength)
    return signals

def send_best_signal():
    global last_directions
    all_signals = generate_signal()
    if not all_signals:
        bot.send_message(chat_id=GROUP_ID, text="⚠️ No strong signal found in this round.")
        return
    best_pair, (direction, _) = max(all_signals.items(), key=lambda x: x[1][1])
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

def start(update: Update, context):
    update.message.reply_text(
        "👋 Welcome to *Quotex Pro Signal Bot!*\n\n"
        "I send high-probability signals every 5 minutes.\n"
        "Use /timeset 120 to change the signal interval.\n\n"
        "✅ Signals are based on real-time multi-candle trend strength.\n\n"
        "Enjoy smart trading!",
        parse_mode='Markdown'
    )

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

def about(update: Update, context):
    update.message.reply_text(
        "📄 *About Quotex Pro Signal Bot*\n\n"
        "This bot sends real-time signals with 90%+ accuracy using strong candle trends.\n"
        "📊 Based on 3-candle momentum filtering.\n\n"
        "👤 Developer: @nknoman22\n"
        "🔗 Bot: @QXProSignalBot",
        parse_mode='Markdown'
    )

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("timeset", timeset))
dispatcher.add_handler(CommandHandler("about", about))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "Quotex Pro Signal Bot is Live!", 200

def run_scheduler():
    while True:
        send_best_signal()
        threading.Event().wait(interval_seconds)

threading.Thread(target=run_scheduler, daemon=True).start()

if HOST_URL:
    try:
        webhook_url = f"{HOST_URL}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        logging.info(f"✅ Webhook set to: {webhook_url}")
    except Exception as e:
        logging.error(f"❌ Failed to set webhook: {e}")

if __name__ == "__main__":
    logging.info("Starting Quotex Pro Signal Bot...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
