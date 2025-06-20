
    if not all_signals:
        bot.send_message(chat_id=GROUP_ID, text="⚠️ No signal generated due to API issue.")
        return

    best_pair = list(all_signals.keys())[0]
    direction = all_signals[best_pair]
    now = datetime.now(TIMEZONE).strftime('%I:%M %p')

    last_directions[now] = (best_pair, direction)

    msg = (
        "\ud83d\udea8 *Trade Signal Alert*\n\n"
        f"\ud83d\udcb9 *Pair:* {best_pair}\n"
        f"\ud83d\udcca *Direction:* {'\ud83d\udcc8' if direction == 'UP' else '\ud83d\udcc9'} {direction}\n"
        f"\ud83d\udd52 *Time:* {now}\n"
        "\u23f1 *Duration:* 1 Minute\n\n"
        "\u26a0\ufe0f Place this trade manually on Quotex!"
    )
    bot.send_message(chat_id=GROUP_ID, text=msg, parse_mode='Markdown')

# --- Telegram Command Handlers ---
def start(update: Update, context):
    update.message.reply_text(
        "\ud83d\udc4b Welcome to *Quotex Pro Signal Bot!*\n\n"
        "I send high-probability signals every 5 minutes.\n"
        "Use /timeset 120 to change the signal interval.\n\n"
        "\u2705 Signals are based on real-time trend analysis.\n\n"
        "Enjoy smart trading!",
        parse_mode='Markdown'
    )

def timeset(update: Update, context):
    global interval_seconds
    try:
        if context.args:
            new_time = int(context.args[0])
            interval_seconds = new_time
            update.message.reply_text(f"\u23f1 Interval set to {interval_seconds} seconds.")
        else:
            raise ValueError
    except Exception:
        update.message.reply_text("\u274c Invalid format. Use: /timeset 120")

def about(update: Update, context):
    update.message.reply_text(
        "\ud83d\udcc4 *About Quotex Pro Signal Bot*\n\n"
        "This bot sends 90%+ accurate signals using real-time market trend data via TwelveData API.\n"
        "\ud83d\udcc8 Based on 1-minute interval candles.\n\n"
        "\ud83d\udc64 Developer: @nknoman22\n"
        "\ud83d\udd17 Bot: @QXProSignalBot",
        parse_mode='Markdown'
    )

# --- Register Command Handlers ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("timeset", timeset))
dispatcher.add_handler(CommandHandler("about", about))

# --- Webhook Endpoints ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK", 200

@app.route("/")
def home():
    return "Quotex Pro Signal Bot is Live!", 200

# --- Scheduler Thread ---
def run_scheduler():
    while True:
        send_best_signal()
        threading.Event().wait(interval_seconds)

threading.Thread(target=run_scheduler, daemon=True).start()

# --- Run Server ---
if __name__ == "__main__":
    logging.info("Starting Quotex Pro Signal Bot...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
    
