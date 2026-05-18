import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions

from utils.config_reader import ConfigReader
from utils.logger import LogGen

logger = LogGen.loggen()


@pytest.fixture(scope="function")
def driver():
    browser = ConfigReader.get("browser").strip().lower()
    base_url = ConfigReader.get("base_url").strip()  # Removed .lower() just in case URLs are case-sensitive

    # 1. Read the value and convert it to lowercase
    headless = ConfigReader.get("headless").strip().lower()

    edge_options = EdgeOptions()
    edge_options.add_argument("--start-maximized")
    edge_options.add_argument("--disable-notifications")
    edge_options.add_argument("--disable-extensions")
    edge_options.add_argument("--disable-infobars")

    # 2. Update the condition to explicitly check for the string "true"
    if headless == "true":
        edge_options.add_argument("--headless")

    driver = webdriver.Edge(options=edge_options)
    driver.get(base_url)

    yield driver

    driver.quit()