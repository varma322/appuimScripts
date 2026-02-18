import time
import re
from selenium.webdriver.common.by import By
from utils.logger import logger
from bot.constants import FLIPKART_PKG
import os
import datetime


def wait_until_any(driver, signals, timeout=15, poll=0.5):
    """Poll page_source until any signal string appears (case-insensitive)."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            source = driver.page_source.upper()
            for sig in signals:
                if sig.upper() in source:
                    return sig
        except Exception:
            pass
        time.sleep(poll)
    return None

def save_screenshot(driver, reason="unknown"):
    os.makedirs("screenshots", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"screenshots/{reason}_{ts}.png"
    driver.save_screenshot(path)
    return path



def close_popups(driver):
    # common close buttons
    candidates = [
        "//*[@content-desc='Close']",
        "//*[@text='✕']",
        "//*[@text='X']",
        "//*[@text='Close']",
        "//*[@text='Not now']",
        "//*[@text='Skip']"
    ]

    for xp in candidates:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            try:
                els[0].click()
                time.sleep(1)
            except:
                pass


def get_price(driver):
    # Scan screen for ₹xxxx
    els = driver.find_elements(By.XPATH, "//*[contains(@text, '₹')]")
    for el in els:
        t = el.get_attribute("text") or ""
        m = re.search(r"₹\s*([0-9,]+)", t)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


# Signals that indicate the product page has loaded
PRODUCT_PAGE_SIGNALS = ["₹", "Buy Now", "Buy at", "Add to cart", "Notify Me", "Sold Out"]


def open_product(driver, url):
    """Open a product page and wait until it finishes loading."""
    driver.execute_script("mobile: shell", {
        "command": "am",
        "args": [
            "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
            FLIPKART_PKG
        ]
    })
    result = wait_until_any(driver, PRODUCT_PAGE_SIGNALS, timeout=15)
    if result is None:
        logger.warning(f"Product page may not have loaded fully for: {url}")


def detect_state(driver):
    """Detect product stock state from a single page_source fetch (1 round-trip)."""
    source = driver.page_source.upper()

    # 1) OUT OF STOCK
    if "NOTIFY ME" in source or "CHANGE ADDRESS" in source:
        return "OUT_OF_STOCK"
    if "SOLD OUT" in source:
        return "OUT_OF_STOCK"

    # 2) NOT DELIVERABLE
    if "NOT DELIVERABLE AT YOUR LOCATION" in source:
        return "NOT_DELIVERABLE"

    # 3) IN STOCK (strongest signal)
    if "BUY AT" in source or "BUY NOW" in source or "ADD TO CART" in source:
        return "IN_STOCK"

    return "UNKNOWN"
