import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from signal_engine import generate_signal
from datetime import datetime
from pytz import timezone

# Load ENV variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
TIMEZONE = timezone('Asia/Dhaka')
INTERVAL = int(os.getenv("INTERVAL", 300))

# Init bot and app
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Scheduler setup
scheduler = BackgroundScheduler(timezone=TIMEZONE)

def send_signal():
    print("📡 Running send_signal function...")
    signal = generate_signal()
    if signal:
        asset, direction, reason = signal
        now = datetime.now(TIMEZONE).strftime('%I:%M %p')
        message = (
            "🚨 *Smart Trade Signal (RSI+EMA)*\n\n"
            f"Pair: `{asset}`\n"
            f"Direction: {'📈 UP' if direction == 'BUY' else '📉 DOWN'}\n"
            f"Reason: {reason}\n"
            f"Time: {now}\n"
            "Duration: 1 Minute\n\n"
            "⚠️ Place trade on Quotex manually."
        )
        print(f"📬 Sending message:\n{message}")
        bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")
    else:
        print("⚠️ No valid signal to send.")

# Schedule job
scheduler.add_job(send_signal, 'interval', seconds=INTERVAL, id='send_signal')
scheduler.start()

# Telegram /start command handler
def start(update: Update, context):
    update.message.reply_text("🤖 RSI+EMA Signal Bot is running!")

# Telegram Dispatcher
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))

# Webhook for Telegram
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

# Manual test route (force signal)
@app.route("/test-signal", methods=["GET"])
def test_signal():
    send_signal()
    return "✅ Signal sent (if valid)", 200

# Root path for Render health check
@app.route("/", methods=["GET"])
def index():
    return "✅ RSI+EMA Signal Bot running."

# App run for local/Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
