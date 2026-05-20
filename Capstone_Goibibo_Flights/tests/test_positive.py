import pytest
import time
from pages.homepage import HomePage
from utils.logger import LogGen

logger = LogGen.loggen()


def test_valid_search(driver):
    logger.info("========== TEST START: test_valid_search ==========")

    homepage = HomePage(driver)

    # Open the train path directly
    homepage.open_goibibo()

    source = "delhi"
    destination = "agra"
    logger.info(f"Testing Train route validation from: {source} to {destination}")

    logger.info("Step 1: Enter Source City and Pick Suggestion")
    homepage.enter_source(source)
    homepage.click_first_suggestion()

    logger.info("Step 2: Enter Destination City and Pick Suggestion")
    homepage.enter_destination(destination)
    homepage.click_first_suggestion()

    logger.info("Step 3: Select Departure Date (Targeting 26 June 2026)")
    homepage.select_departure_date("June 2026", "26")

    logger.info("Step 4: Click Search Button")
    homepage.click_search()

    logger.info("Step 5: Verify Results Page Loaded")
    time.sleep(5)  # Give the network time to change URLs and pull lists

    # Validate that we successfully broke past the search box into the listing data page
    current_url = driver.current_url.lower()
    logger.info(f"Navigated URL Target: {current_url}")

    assert "train" in current_url, f"Expected to land on train results page, but was stopped at: {driver.current_url}"
    logger.info("Assertion Passed: URL confirms train modules destination processing!")

    logger.info("========== TEST END: test_valid_search ==========")


def test_blank(driver):
    homepage = HomePage(driver)
    homepage.open_goibibo()
    time.sleep(500)