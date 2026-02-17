import os
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options

load_dotenv()


def create_driver():
    appium_server = os.getenv("APPIUM_SERVER", "http://127.0.0.1:4723")

    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.device_name = "RealmeX2"
    opts.automation_name = "UiAutomator2"

    # Skip operations that fail without WRITE_SECURE_SETTINGS
    opts.set_capability("ignoreHiddenApiPolicyError", True)
    opts.set_capability("skipDeviceInitialization", True)
    opts.set_capability("skipUnlock", True)
    opts.set_capability("autoGrantPermissions", False)


    # IMPORTANT: keep login session
    opts.no_reset = True
    opts.new_command_timeout = 300

    driver = webdriver.Remote(appium_server, options=opts)
    return driver
