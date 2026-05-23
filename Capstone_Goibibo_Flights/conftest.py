# ===========================================================
# IMPORTS
# ===========================================================
import os
import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from utils.config_reader import ConfigReader
from utils.logger import LogGen
from utils.screenshot import ScreenshotUtil

logger = LogGen.loggen()

# ===========================================================
# DRIVER
# ===========================================================
@pytest.fixture(scope="function")
def driver():
    browser = ConfigReader.get("browser").strip().lower()
    base_url = ConfigReader.get("base_url").strip()
    headless = ConfigReader.get("headless").strip().lower()

    edge_options = EdgeOptions()
    edge_options.add_argument("--start-maximized")
    edge_options.add_argument("--disable-notifications")
    edge_options.add_argument("--disable-extensions")
    edge_options.add_argument("--disable-infobars")
    edge_options.add_argument("--disable-popup-blocking")

    if headless == "true":
        edge_options.add_argument("--headless")

    driver = webdriver.Edge(options=edge_options)

    # Ensure this line lives inside your driver setup fixture block
    driver.implicitly_wait(5)  # Global polling buffer for element synchronization

    driver.get(base_url)

    yield driver

    driver.quit()


# Core Upgrade: Automatically capture screenshot inside Allure if any test case crashes
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Dynamic fallback check across setup, call, or teardown failures
    if rep.failed:
        try:
            if "driver" in item.fixturenames:
                web_driver = item.funcargs["driver"]
                # Use your existing utility to capture and attach the failure screen
                ScreenshotUtil.capture_screenshot(web_driver, screenshot_name=f"CRITICAL_FAILURE_{item.name}")
        except Exception as e:
            logger.error(f"Failed to automatically attach failure layout anchor to Allure: {e}")