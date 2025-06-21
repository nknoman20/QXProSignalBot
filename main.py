import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from signal_engine import generate_signal
from datetime import datetime
from pytz import timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
TIMEZONE = timezone('Asia/Dhaka')
INTERVAL = int(os.getenv("INTERVAL", 300))

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler(timezone=TIMEZONE)

def send_signal():
    signal = generate_signal()
    if signal:
        asset, direction, reason = signal
        now = datetime.now(TIMEZONE).strftime('%I:%M %p')
        message = (
            "🚨 *Smart Trade Signal (RSI+EMA)*

"
            f"Pair: `{asset}`
"
            f"Direction: {'📈 UP' if direction == 'BUY' else '📉 DOWN'}
"
            f"Reason: {reason}
"
            f"Time: {now}
"
            "Duration: 1 Minute

"
            "⚠️ Place trade on Quotex manually."
        )
        bot.send_message(chat_id=GROUP_ID, text=message, parse_mode="Markdown")

scheduler.add_job(send_signal, 'interval', seconds=INTERVAL, id='send_signal')
scheduler.start()

def start(update: Update, context):
    update.message.reply_text("🤖 RSI+EMA Signal Bot is running!")

dispatcher = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "✅ RSI+EMA Signal Bot running."
