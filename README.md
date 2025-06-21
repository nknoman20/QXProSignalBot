# Quotex Pro Signal Bot (RSI + EMA)

This bot sends smart 1-minute trading signals using live RSI and EMA crossover logic.

## Features
- RSI (14) + EMA(9/21) based confirmation
- Sends signal to Telegram group via webhook
- Real-time market data from TwelveData

## Deploy Instructions

1. Upload to GitHub
2. Connect repo to [Render.com](https://render.com)
3. Set secrets in environment:
   - `BOT_TOKEN`
   - `GROUP_ID`
   - `TWELVEDATA_API_KEY`
   - `INTERVAL` (optional, default: 300)
4. Deploy as Web Service (uses `render.yaml`)

Enjoy smart signals!
