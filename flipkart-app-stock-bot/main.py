import json
import os
import time
from dotenv import load_dotenv
from bot.address_switcher import select_saved_address

from bot.constants import FLIPKART_PKG
from bot.appium_driver import create_driver
from bot.flipkart_app_checker import open_product, detect_state, get_price, close_popups, save_screenshot
from bot.telegram_notifier import send_telegram
from bot.state_store import load_state, save_state, update_product_state, mark_alerted
from bot.scheduler import sleep_random
from utils.logger import logger
from utils.cleanup import cleanup_old_screenshots

HEARTBEAT_FILE = "heartbeat.txt"

load_dotenv()

REMINDER_SECONDS = int(os.getenv("REMINDER_SECONDS", "2700"))
ADDRESSES = [a.strip() for a in os.getenv("ADDRESSES", "Kishore,Varma Kamadi").split(",")]


def load_products():
    with open("config/products.json", "r", encoding="utf-8") as f:
        return json.load(f)


def format_msg(kind, product_name, status, price, url, extra=""):
    return (
        f"{kind}\n\n"
        f"{product_name}\n"
        f"Status: {status}\n"
        f"Price: {price}\n"
        f"{extra}\n\n"
        f"{url}"
    )


def write_heartbeat():
    """Write current timestamp to heartbeat file for watchdog."""
    try:
        with open(HEARTBEAT_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def main():
    products = load_products()

    print("🚀 Starting Flipkart App Stock Bot")

    while True:
        driver = None
        try:
            write_heartbeat()
            cleanup_old_screenshots()
            driver = create_driver()
            logger.info("🔄 Home screen")
            state = load_state()

            for addr in ADDRESSES:
                logger.info(f"📍 Switching address -> {addr}")
                select_saved_address(driver, addr)

                for p in products:
                    name = p["name"]
                    url = p["url"].split("?")[0]
                    target = int(p.get("target_price", 10**9))

                    logger.info(f"🔎 Checking: {name} @ {addr}")

                    open_product(driver, url)
                    logger.info("🔄 Product opened")
                    close_popups(driver)
                    logger.info("🔄 Popups closed")

                    status = detect_state(driver)
                    price = get_price(driver)
                    logger.info(f"🔄 Status: {status}, Price: {price}")
                    write_heartbeat()

                    # UNKNOWN / AMBIGUOUS
                    if status in ["UNKNOWN", "AMBIGUOUS"]:
                        path = save_screenshot(driver, f"{status.lower()}_{addr}")
                        send_telegram(
                            f"⚠ {status} UI detected\n"
                            f"{name}\n"
                            f"Address: {addr}\n"
                            f"Price: {price}\n"
                            f"Screenshot: {path}\n"
                            f"{url}"
                        )
                        continue

                    prev, cur = update_product_state(state, f"{url}::{addr}", status, price)

                    now = time.time()
                    last_alert = cur.get("last_alert", 0)

                    if status in ["OUT_OF_STOCK", "NOT_DELIVERABLE"]:
                        continue

                    if status == "IN_STOCK":

                        # PRICE DROP
                        if price is not None and price <= target:
                            send_telegram(
                                format_msg(
                                    "🔥 PRICE DROP ALERT",
                                    name,
                                    status,
                                    price,
                                    url,
                                    extra=f"Address: {addr}\nTarget was ₹{target}"
                                )
                            )
                            mark_alerted(state, f"{url}::{addr}")
                            logger.info("🔄 Price drop alert sent")
                            continue

                        # RESTOCK
                        if prev.get("last_status") != "IN_STOCK":
                            send_telegram(
                                format_msg(
                                    "🔥 RESTOCK ALERT",
                                    name,
                                    status,
                                    price,
                                    url,
                                    extra=f"Address: {addr}\nProduct is BUYABLE now"
                                )
                            )
                            mark_alerted(state, f"{url}::{addr}")
                            logger.info("🔄 Restock alert sent")
                            continue

                        # REMINDER
                        if now - last_alert > REMINDER_SECONDS:
                            send_telegram(
                                format_msg(
                                    "⏰ REMINDER",
                                    name,
                                    status,
                                    price,
                                    url,
                                    extra=f"Address: {addr}\nStill in stock"
                                )
                            )
                            mark_alerted(state, f"{url}::{addr}")
                            logger.info("🔄 Reminder alert sent")

            save_state(state)

        except Exception as e:
            print("❌ Bot error:", e)

        finally:
            if driver:
                try:
                    driver.terminate_app(FLIPKART_PKG)
                    logger.info("🔄 Flipkart app closed")
                    driver.quit()
                except:
                    pass

        # Random sleep

        sleep_random(8, 15)


if __name__ == "__main__":
    main()
