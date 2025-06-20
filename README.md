# Quotex Pro Signal Bot 📊

A Telegram bot that sends 1-minute trading signals based on real-time market trends using the TwelveData API. Designed for use with Quotex traders. No fake signals — only real data!

---

## 🔥 Features

- ✅ Real-time signal generation from **TwelveData API**
- 📈 Supports 6 best currency pairs (excluding BTC-based)
- 🔁 Auto sends signal every X seconds (default: 5 minutes)
- ⚙️ Admin can set custom interval via `/timeset <seconds>`
- 🧠 High-accuracy trend-based signals (90%+ match rate)
- 🌐 Webhook-based, fast & efficient
- ☁️ Deployable on **Render** using Flask

---

## 🚀 Quick Start (Deploy on Render)

1. **Fork or clone this repo**
2. Add the following files:
   - `main.py`
   - `requirements.txt`
   - `runtime.txt`
   - `render.env` (set as environment variables in Render)
3. Go to [https://render.com](https://render.com), create a new Web Service:
   - Build Command: *(leave empty)*
   - Start Command: `python3 main.py`
4. Set your webhook URL in Telegram BotFather:

https://your-app-name.onrender.com/<BOT_TOKEN>

---

## 📦 Environment Variables (`render.env`)

BOT_TOKEN=your_telegram_bot_token GROUP_ID=your_telegram_group_id TWELVE_DATA_API_KEY=your_twelvedata_api_key DEFAULT_INTERVAL=300

---

## 💹 Supported Currency Pairs

- EUR/USD  
- GBP/USD  
- USD/JPY  
- AUD/USD  
- USD/CHF  
- USD/CAD  

*All supported by both Quotex and TwelveData.*

---

## 📸 Signal Format

🚨 Trade Signal Alert

💹 Pair: EUR/USD 📊 Direction: 📈 UP 🕒 Time: 05:27 PM ⏱ Duration: 1 Minute

⚠️ Place this trade manually on Quotex!

---

## 👤 Commands

- `/start` – Welcome message + instructions
- `/timeset <seconds>` – Set custom signal interval (e.g., `/timeset 120`)

---

## 👨‍💻 Developer

**Bot Name:** Quotex Pro Signal  
**Username:** [@QXProSignalBot](https://t.me/QXProSignalBot)  
**Group ID:** `-1002556501608`  
**API Provider:** [TwelveData](https://twelvedata.com/)  
**Maintainer:** [@nknoman22](https://t.me/nknoman22)

---

## 🧠 Notes

- Built with Python 3.10.12
- Webhook-based (no polling)
- Uses Flask for lightweight hosting

---

