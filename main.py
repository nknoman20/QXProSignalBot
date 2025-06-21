import os
import logging
import requests
import threading
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from datetime import datetime, timedelta
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
DEFAULT_INTERVAL = int(os.getenv("DEFAULT_INTERVAL", 300))
QUOTEX_OFFSET = int(os.getenv("QUOTEX_OFFSET", 10))  # seconds offset for Quotex clock
TIMEZONE = timezone("Asia/Dhaka")
HOST_URL = os.getenv("HOST_URL")
PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, update_queue=None, workers=4, use_context=True)
logging.basicConfig(level=logging.INFO)

# ✅ Correct Finnhub symbols (OANDA)
PAIRS = {
    "EUR_USD": "EUR/USD",
    "GBP_USD": "GBP/USD",
    "USD_JPY": "USD/JPY",
    "AUD_USD": "AUD/USD"
}

interval_seconds = DEFAULT_INTERVAL

def get_candle_data(symbol):
    url = f"https://finnhub.io/api/v1/forex/candle?symbol=OANDA:{symbol}&resolution=1&count=5&token={FINNHUB_API_KEY}"
    try:
        res = requests.get(url).json()
        if res.get("s") != "ok":
            raise ValueError("Invalid response status")
        return res
    except Exception as e:
        logging.error(f"Error fetching candle data for {symbol}: {e}")
        return None

def analyze_trend(symbol):
    data = get_candle_data(symbol)
    if not data:
        return None

    closes = data.get("c", [])
    if len(closes) < 4:
        logging.error(f"Not enough candle data for {symbol}")
        return None

    diff1 = closes[-1] - closes[-2]
    diff2 = closes[-2] - closes[-3]
    diff3 = closes[-3] - closes[-4]

    threshold = 0.0001  # Forex pairs move small
    if diff1 > threshold and diff2 > threshold and diff3 > threshold:
        return "UP"
    elif diff1 < -threshold and diff2 < -threshold and diff3 < -threshold:
        return "DOWN"
    else:
        return None

def generate_signals():
    signals = {}
    for symbol, display_name in PAIRS.items():
        trend = analyze_trend(symbol)
        if trend:
            signals[display_name] = trend
    return signals

def send_signal():
    signals = generate_signals()
    if not signals:
        bot.send_message(chat_id=GROUP_ID, text="⚠️ No strong signals detected this round.")
        return

    pair, direction = next(iter(signals.items()))
    now = datetime.now(TIMEZONE) + timedelta(seconds=QUOTEX_OFFSET)
    entry_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    entry_time_str = entry_time.strftime("%I:%M %p")

    emoji = "📈" if direction == "UP" else "📉"
    message = (
        f"🚨 Trade Signal Alert\n\n"
        f"💹 Pair: {pair}\n"
        f"📊 Direction: {emoji} {direction}\n"
        f"🕒 Entry Time: {entry_time_str}\n"
        f"⏱ Duration: 1 Minute\n\n"
        f"⚠️ Place this trade manually on Quotex!\n"
        f"🕰 Quotex Clock Adjusted ✅"
    )
    bot.send_message(chat_id=GROUP_ID, text=message)

def start(update: Update, context):
    update.message.reply_text(
        "👋 Welcome to Quotex Pro Signal Bot!\n"
        "I send real-time, accurate signals every 5 minutes.\n"
        "Use /timeset <seconds> to change interval.\n"
        "Trade smart, trade safe!"
    )

def timeset(update: Update, context):
    global interval_seconds
    try:
        if context.args:
            new_interval = int(context.args[0])
            interval_seconds = new_interval
            update.message.reply_text(f"✅ Interval changed to {interval_seconds} seconds.")
        else:
            update.message.reply_text("Usage: /timeset <seconds>")
    except Exception:
        update.message.reply_text("❌ Invalid input. Use: /timeset <seconds>")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("timeset", timeset))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def index():
    return "✅ Quotex Pro Signal Bot is Running!", 200

def scheduler_thread():
    while True:
        send_signal()
        threading.Event().wait(interval_seconds)

if __name__ == "__main__":
    if HOST_URL:
        webhook_url = f"{HOST_URL}/{BOT_TOKEN}"
        bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook set to {webhook_url}")

    threading.Thread(target=scheduler_thread, daemon=True).start()
    logging.info("Starting Flask server...")
    app.run(host="0.0.0.0", port=PORT)
