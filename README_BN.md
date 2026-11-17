# Telegram Cloud Monitor

এটি Telegram-ভিত্তিক **monitoring-only** Worker। এটি game account তৈরি/লগইন,
match automation, token refresh, ban এড়ানো বা game client control করে না।
Telegram নিজে hosting server নয়; কোডটি Render/Railway-এর মতো Background Worker-এ
deploy করতে হবে।

## সেটআপ
1. Telegram-এর `@BotFather`-এ `/newbot` দিয়ে bot তৈরি করুন।
2. `.env.example` কপি করে `.env` বানান।
3. `TELEGRAM_BOT_TOKEN`-এ BotFather token এবং `TELEGRAM_ALLOWED_CHAT_IDS`-এ
   নিজের numeric Telegram chat ID দিন।
4. লোকালি:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   set -a; source .env; set +a
   python -m app.bot
   ```
5. Cloud-এ ZIP/GitHub private repo deploy করে Build command দিন
   `pip install -r requirements.txt` এবং Start command দিন `python -m app.bot`।
   Token ও chat ID hosting-এর Environment Variables/Secrets-এ দিন; ZIP/GitHub-এ নয়।

## Commands
- `/start`
- `/status` — CPU, RAM, disk, uptime
- `/health` — optional `HEALTH_URL` check
- `/help`

Bot token কখনো কারও সঙ্গে শেয়ার করবেন না। ফাঁস হলে BotFather থেকে revoke করুন।
মূল GuildGlory ZIP-এর Android-specific `.so` modules Linux hosting-এ চলবে না;
তার জন্য Linux-compatible build বা source প্রয়োজন।
