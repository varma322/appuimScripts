import time
from selenium.webdriver.common.by import By
from bot.flipkart_app_checker import close_popups, save_screenshot

FLIPKART_PKG = "com.flipkart.android"


# def go_home(driver):
#     # Most reliable launch
#     driver.execute_script("mobile: shell", {
#         "command": "monkey",
#         "args": [
#             "-p", FLIPKART_PKG,
#             "-c", "android.intent.category.LAUNCHER",
#             "1"
#         ]
#     })
#     time.sleep(4)

#     # clear stacked screens
#     for _ in range(2):
#         driver.back()
#         time.sleep(0.8)


def wait_for_text(driver, text, timeout=8):
    start = time.time()
    while time.time() - start < timeout:
        if driver.find_elements(By.XPATH, f"//*[contains(@text,'{text}')]"):
            return True
        time.sleep(0.4)
    return False


def tap_address_bar(driver):
    # best selector: the dropdown arrow near address bar
    candidates = [
        'new UiSelector().textContains("WORK")',
        'new UiSelector().textContains("HOME")',
        'new UiSelector().textContains("Select delivery location")',
        'new UiSelector().textContains("HIG-111")',
        'new UiSelector().textContains("Km-111")',
    ]
    time.sleep(5)
    for sel in candidates:
        try:
            el = driver.find_element(By.ANDROID_UIAUTOMATOR, sel)
            el.click()
            time.sleep(1.5)
            return True
        except:
            pass

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
        time.sleep(3)
    except:
        path = save_screenshot(driver, f"address_not_found_{address_name}")
        raise Exception(f"Address '{address_name}' not found. Screenshot: {path}")

    # Close sheet if still open
    driver.back()
    time.sleep(1)

    return True



# def go_home(driver):
#     # Force open Flipkart home
#     driver.execute_script("mobile: shell", {
#         "command": "am",
#         "args": [
#             "start",
#             "-n",
#             "com.flipkart.android/.activity.HomeFragmentHolderActivity"
#         ]
#     })
#     time.sleep(4)
# def go_home(driver):
    # Most reliable way to open Flipkart home
# def go_home(driver):
#     # Most reliable way to open Flipkart home
#     driver.execute_script("mobile: shell", {
#         "command": "monkey",
#         "args": [
#             "-p", "com.flipkart.android",
#             "-c", "android.intent.category.LAUNCHER",
#             "1"
#         ]
#     })
#     time.sleep(4)

def force_home(driver):
    # 1) Kill Flipkart completely
    driver.execute_script("mobile: shell", {
        "command": "am",
        "args": ["force-stop", FLIPKART_PKG]
    })
    time.sleep(2)

    # 2) Launch Flipkart from launcher (HOME)
    driver.execute_script("mobile: shell", {
        "command": "monkey",
        "args": [
            "-p", FLIPKART_PKG,
            "-c", "android.intent.category.LAUNCHER",
            "1"
        ]
    })
    time.sleep(6)