import os, logging, platform, shutil
from datetime import datetime, timezone
import psutil
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED = {int(v.strip()) for v in os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS","").split(",") if v.strip()}
SERVICE_NAME = os.environ.get("SERVICE_NAME", "Cloud host")
HEALTH_URL = os.environ.get("HEALTH_URL", "").strip()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(), logging.FileHandler("telegram_monitor.log", encoding="utf-8")])
log = logging.getLogger("monitor")

def allowed(update):
    return bool(update.effective_chat and update.effective_chat.id in ALLOWED)

async def deny(update):
    if update.message: await update.message.reply_text("Access denied: this Telegram chat is not allowlisted.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await deny(update)
    await update.message.reply_text("Cloud monitor online. Commands: /status, /health, /help\nMonitoring only: no game-account, match, token-refresh or game-client controls.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await deny(update)
    await update.message.reply_text("/status — CPU/RAM/disk/uptime\n/health — optional health URL\n/help — commands")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await deny(update)
    vm = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    uptime = datetime.now(timezone.utc) - datetime.fromtimestamp(psutil.boot_time(), timezone.utc)
    msg = (f"☁️ {SERVICE_NAME}\nHost: {platform.node()}\nOS: {platform.system()} {platform.release()}\n"
           f"Python: {platform.python_version()}\nCPU: {psutil.cpu_percent(interval=0.4)}%\n"
           f"RAM: {vm.percent}% ({vm.used//2**20}/{vm.total//2**20} MB)\n"
           f"Disk: {disk.used*100//disk.total}% ({disk.free//2**30} GB free)\n"
           f"Uptime: {str(uptime).split('.')[0]}\n"
           f"Checked: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await update.message.reply_text(msg)

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await deny(update)
    if not HEALTH_URL:
        return await update.message.reply_text("HEALTH_URL is not configured.")
    try:
        import aiohttp
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as s:
            async with s.get(HEALTH_URL) as r:
                await update.message.reply_text(f"Health endpoint: HTTP {r.status}\n{(await r.text())[:400]}")
    except Exception as exc:
        log.exception("Health check failed")
        await update.message.reply_text(f"Health check failed: {type(exc).__name__}")

def main():
    if not ALLOWED: raise RuntimeError("Set TELEGRAM_ALLOWED_CHAT_IDS first.")
    app = Application.builder().token(TOKEN).build()
    for cmd, fn in [("start", start), ("help", help_cmd), ("status", status), ("health", health)]:
        app.add_handler(CommandHandler(cmd, fn))
    log.info("Telegram monitor started")
    app.run_polling()

if __name__ == "__main__": main()
  
