import json
import os
import time
from dotenv import load_dotenv

from bot.appium_driver import create_driver
from bot.flipkart_app_checker import open_product, detect_state, get_price, close_popups, save_screenshot
from bot.telegram_notifier import send_telegram
from bot.state_store import update_product_state, mark_alerted
from bot.scheduler import sleep_random

load_dotenv()

REMINDER_SECONDS = int(os.getenv("REMINDER_SECONDS", "2700"))


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


def main():
    products = load_products()

    print("🚀 Starting Flipkart App Stock Bot")

    while True:
        driver = None
        try:
            driver = create_driver()

            for p in products:
                name = p["name"]
                url = p["url"].split("?")[0]
                target = int(p.get("target_price", 10**9))

                print(f"\n🔎 Checking: {name}")
                open_product(driver, url)
                close_popups(driver)
                status = detect_state(driver)
                price = get_price(driver)
                if status == "UNKNOWN":
                    path = save_screenshot(driver, "unknown_ui")
                    send_telegram(f"⚠ UNKNOWN UI detected\n{name}\nScreenshot saved: {path}\n{url}")
                    continue

                print("STATUS:", status, "| PRICE:", price)

                prev, cur = update_product_state(url, status, price)

                now = time.time()
                last_alert = cur.get("last_alert", 0)

                # ----------------------------
                # Alert Rules
                # ----------------------------

                # If not buyable, skip alerts
                if status in ["OUT_OF_STOCK", "NOT_DELIVERABLE"]:
                    continue

                # IN STOCK alerts
                if status == "IN_STOCK":

                    # 1) PRICE DROP
                    if price is not None and price <= target:
                        msg = format_msg(
                            "🔥 PRICE DROP ALERT",
                            name,
                            status,
                            price,
                            url,
                            extra=f"Target was ₹{target}"
                        )
                        send_telegram(msg)
                        mark_alerted(url)
                        continue

                    # 2) FIRST RESTOCK
                    if prev.get("last_status") != "IN_STOCK":
                        msg = format_msg(
                            "🔥 RESTOCK ALERT",
                            name,
                            status,
                            price,
                            url,
                            extra="Product is BUYABLE now"
                        )
                        send_telegram(msg)
                        mark_alerted(url)
                        continue

                    # 3) REMINDER
                    if now - last_alert > REMINDER_SECONDS:
                        msg = format_msg(
                            "⏰ REMINDER",
                            name,
                            status,
                            price,
                            url,
                            extra="Still in stock — don’t miss it"
                        )
                        send_telegram(msg)
                        mark_alerted(url)

        except Exception as e:
            print("❌ Bot error:", e)

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

        # Random sleep
        sleep_random(8, 15)


if __name__ == "__main__":
    main()
