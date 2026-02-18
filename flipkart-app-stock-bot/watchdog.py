import subprocess
import time
import sys

from bot.telegram_notifier import send_telegram

CHECK_INTERVAL = 30
RESTART_DELAY = 5


def start_bot():
    return subprocess.Popen([sys.executable, "main.py"])


def main():
    print("🛡 Watchdog started")
    bot = start_bot()

    while True:
        time.sleep(CHECK_INTERVAL)

        if bot.poll() is not None:
            msg = "⚠ Watchdog: bot crashed, restarting now..."
            print(msg)
            try:
                send_telegram(msg)
            except:
                pass

            time.sleep(RESTART_DELAY)
            bot = start_bot()


if __name__ == "__main__":
    main()
