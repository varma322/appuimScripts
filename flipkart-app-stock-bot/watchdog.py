import subprocess
import time
import os
import sys

CHECK_INTERVAL = 60  # watchdog checks every 60s
RESTART_DELAY = 5

def start_bot():
    return subprocess.Popen([sys.executable, "main.py"])

def main():
    print("🛡 Watchdog started")
    bot = start_bot()

    while True:
        time.sleep(CHECK_INTERVAL)

        # if bot exited -> restart
        if bot.poll() is not None:
            print("⚠ Bot crashed. Restarting...")
            time.sleep(RESTART_DELAY)
            bot = start_bot()

if __name__ == "__main__":
    main()
