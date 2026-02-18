import time
from selenium.webdriver.common.by import By
from bot.flipkart_app_checker import close_popups, save_screenshot, wait_until_any
from bot.constants import FLIPKART_PKG
from utils.logger import logger



def wait_for_text(driver, text, timeout=8):
    """Poll until an element containing `text` appears on screen."""
    start = time.time()
    while time.time() - start < timeout:
        if driver.find_elements(By.XPATH, f"//*[contains(@text,'{text}')]"):
            return True
        time.sleep(0.4)
    return False


ADDRESS_BAR_SELECTORS = [
    'new UiSelector().textContains("WORK")',
    'new UiSelector().textContains("HOME")',
    'new UiSelector().textContains("Select delivery location")',
    'new UiSelector().textContains("HIG-111")',
    'new UiSelector().textContains("Km-111")',
]


def tap_address_bar(driver, timeout=10):
    """Poll for address bar candidates instead of a fixed sleep."""
    start = time.time()
    while time.time() - start < timeout:
        for sel in ADDRESS_BAR_SELECTORS:
            try:
                el = driver.find_element(By.ANDROID_UIAUTOMATOR, sel)
                el.click()
                time.sleep(1)  # brief settle after click
                return True
            except Exception:
                pass
        time.sleep(0.5)
    return False


def select_saved_address(driver, address_name: str):
    
    force_home(driver)
    close_popups(driver)

    # Open selector
    if not tap_address_bar(driver):
        path = save_screenshot(driver, "address_bar_not_found")
        raise Exception(f"Address bar not found. Screenshot: {path}")

    # Wait for sheet
    if not wait_for_text(driver, "Select delivery address", timeout=8):
        path = save_screenshot(driver, "address_sheet_not_opening")
        raise Exception(f"Address sheet not opening. Screenshot: {path}")

    # Click address
    try:
        addr = driver.find_element(
            By.ANDROID_UIAUTOMATOR,
            f'new UiSelector().textContains("{address_name}")'
        )
        addr.click()
        # Wait until the address sheet closes (home content reappears)
        wait_for_text(driver, "Explore", timeout=5)
    except Exception:
        path = save_screenshot(driver, f"address_not_found_{address_name}")
        raise Exception(f"Address '{address_name}' not found. Screenshot: {path}")

    # Close sheet if still open
    driver.back()
    time.sleep(0.5)

    return True



# Signals that indicate Flipkart home screen has loaded
HOME_SIGNALS = ["Explore", "Search", "Categories", "HOME", "WORK"]


def force_home(driver):
    """Kill and relaunch Flipkart, waiting for home screen to appear."""
    # 1) Kill Flipkart completely
    driver.execute_script("mobile: shell", {
        "command": "am",
        "args": ["force-stop", FLIPKART_PKG]
    })
    time.sleep(1)  # brief pause for process to die

    # 2) Launch Flipkart from launcher (HOME)
    driver.execute_script("mobile: shell", {
        "command": "monkey",
        "args": [
            "-p", FLIPKART_PKG,
            "-c", "android.intent.category.LAUNCHER",
            "1"
        ]
    })

    # 3) Wait for home screen signal instead of fixed sleep
    result = wait_until_any(driver, HOME_SIGNALS, timeout=15)
    if result is None:
        logger.warning("Home screen may not have loaded fully")