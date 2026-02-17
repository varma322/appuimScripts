import time
import re
from selenium.webdriver.common.by import By


FLIPKART_PKG = "com.flipkart.android"


def exists_contains(driver, text):
    xpath = f"//*[contains(@text, '{text}')]"
    return len(driver.find_elements(By.XPATH, xpath)) > 0


def get_price(driver):
    # Scan screen for ₹xxxx
    els = driver.find_elements(By.XPATH, "//*[contains(@text, '₹')]")
    for el in els:
        t = el.get_attribute("text") or ""
        m = re.search(r"₹\s*([0-9,]+)", t)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


def open_product(driver, url):
    # More reliable than mobile:deepLink sometimes
    driver.execute_script("mobile: shell", {
        "command": "am",
        "args": [
            "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
            FLIPKART_PKG
        ]
    })
    time.sleep(10)


def detect_state(driver):
    # 1) OUT OF STOCK
    if exists_contains(driver, "Notify Me") or exists_contains(driver, "NOTIFY ME") or exists_contains(driver, "Change Address") or exists_contains(driver, "CHANGE ADDRESS "):
        return "OUT_OF_STOCK"

    if exists_contains(driver, "Sold Out") or exists_contains(driver, "SOLD OUT"):
        return "OUT_OF_STOCK"

    # 2) NOT DELIVERABLE
    if exists_contains(driver, "Not deliverable at your location"):
        return "NOT_DELIVERABLE"

    # 3) IN STOCK (strongest signal)
    if exists_contains(driver, "Buy at") or exists_contains(driver, "Buy Now") or exists_contains(driver, "Add to cart") or exists_contains(driver, "ADD TO CART"):
        return "IN_STOCK"

    return "UNKNOWN"
