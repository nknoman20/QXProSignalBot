# Elite Quotex Signal Bot 🤖

A Telegram bot that sends random 1-minute trading signals every 5 minutes (or your custom interval) to a Telegram group.

## ✅ Features

- Sends random signals like `EUR/USD UP` every few minutes
- `/start` command shows welcome + usage
- `/timeset <seconds>` allows manual control over frequency
- Deployed using **Webhook + Flask** (not polling)
- Render + GitHub compatible

## 🚀 Deployment (Render)

1. Upload all files to a GitHub repository
2. Create a **Web Service** on [Render](https://render.com)
3. Add environment variables via `render.env`
4. Use `python main.py` as start command
5. After deploy, set your bot's webhook:

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-render-url.onrender.com/<YOUR_BOT_TOKEN>
```

Example:
```
https://api.telegram.org/bot8050053152:AAE3ZJ1nOirlpyY-fZxevXR4gJ2AN2zs5M0/setWebhook?url=https://elitequotex.onrender.com/8050053152:AAE3ZJ1nOirlpyY-fZxevXR4gJ2AN2zs5M0
```

## ✅ Usage

- `/start` → Shows welcome instructions
- `/timeset 120` → Changes signal interval to every 2 minutes

## 👤 Created for: @EliteQuotexBot