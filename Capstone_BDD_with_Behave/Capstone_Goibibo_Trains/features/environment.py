import os
import sys

import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.config_reader import ConfigReader
from utils.logger import LogGen
from utils.screenshot import ScreenshotUtil

logger = LogGen.loggen()


def _as_bool(value):
    return str(value).strip().lower() in ("true", "1", "yes", "y")


def _build_driver(browser, headless):
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-popup-blocking")
        if headless:
            options.add_argument("--headless=new")
        return webdriver.Chrome(options=options)

    options = EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    if headless:
        options.add_argument("--headless")
    return webdriver.Edge(options=options)


def before_all(context):
    os.makedirs(os.path.join(PROJECT_ROOT, "logs"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "reports", "screenshots"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, "reports", "allure-results"), exist_ok=True)
    logger.info("BDD Behave Allure framework initialized")


def before_scenario(context, scenario):
    logger.info("========================================")
    logger.info(f"STARTING SCENARIO: {scenario.name}")

    browser = ConfigReader.get("browser").strip().lower()
    base_url = ConfigReader.get("base_url").strip()
    wait_seconds = int(ConfigReader.get("wait") or 5)
    headless = _as_bool(ConfigReader.get("headless"))

    context.driver = _build_driver(browser, headless)
    context.driver.implicitly_wait(wait_seconds)
    context.driver.get(base_url)
    logger.info(f"Browser launched: {browser}; base url: {base_url}")


def after_step(context, step):
    if str(step.status).lower() == "failed":
        logger.error(f"STEP FAILED: {step.name}")
        ScreenshotUtil.capture_screenshot(context.driver, f"FAILED_STEP_{step.name}")


def after_scenario(context, scenario):
    status = str(scenario.status).lower()
    logger.info(f"SCENARIO STATUS: {scenario.status}")

    if "failed" in status:
        ScreenshotUtil.capture_screenshot(context.driver, f"FAILED_SCENARIO_{scenario.name}")
    else:
        try:
            ScreenshotUtil.capture_screenshot(context.driver, f"PASSED_SCENARIO_{scenario.name}")
        except Exception as error:
            logger.warning(f"Could not capture passed scenario screenshot: {error}")

    log_path = os.path.join(PROJECT_ROOT, "logs", "automation.log")
    if os.path.exists(log_path):
        try:
            allure.attach.file(
                log_path,
                name="automation.log",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as error:
            logger.warning(f"Could not attach log file to Allure: {error}")

    context.driver.quit()
    logger.info("Browser closed")
    logger.info("========================================")
