# IMPORTS FOR ALL TEST CASES
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages import homepage
from pages.homepage import HomePage
from pages.results_page import ResultsPage
from utils.logger import LogGen
from utils.csv_reader import CSVReader
import csv
import os
import random
import allure

logger = LogGen.loggen()

# READ FROM CSV FILES
# SEPARATE CSV FILES FOR EACH INDEPENDENT CHECKPOINT
train_data = CSVReader.read_csv("search_trains.csv")
class_data = CSVReader.read_csv("filter_class.csv")
time_filter_data = CSVReader.read_csv("filter_time.csv")
station_filter_data = CSVReader.read_csv("filter_station.csv")
dep_sort_data = CSVReader.read_csv("sort_departure.csv")
arr_sort_data = CSVReader.read_csv("sort_arrival.csv")
invalid_date_data = CSVReader.read_csv("invalid_date.csv")
no_trains_data    = CSVReader.read_csv("no_trains.csv")


def search_for_trains(driver):
    homepage = HomePage(driver)
    homepage.popup_close()
    homepage.train_data_for_csv(train_data[0])

def read_single_row_csv(file_name):
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", file_name)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing expected CSV test data file at: {csv_path}")
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return next(reader)


def test_opening(driver):
    search_for_trains(driver)


# POSITIVE TESTS

# TEST 1: COACH CLASS FILTER
@pytest.mark.parametrize("data", class_data)
@allure.feature("Positive Testing")
@allure.story("Coach Class Filtering Validation")
def test_coach_class_filter(driver, data):

    logger.info("STARTING EXECUTION: Test 1 - Coach Class Filter Validation")
    search_for_trains(driver)

    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    results_page.apply_dynamic_class_filter(data['ClassFilterLabel'])
    results_page.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class,'TrainCard_trnCrd__')]")))

    is_verified = results_page.verify_class_present_in_results(data['ClassExpectedCode'])
    assert is_verified, f"Filter validation failed! Active listings did not map to {data['ClassExpectedCode']}."
    logger.info("SUCCESS: Test 1 - Coach Class Filter verified successfully.")

# TEST 2: DEPARTURE TIME FILTER
@pytest.mark.parametrize("data", time_filter_data)
@allure.feature("Positive Testing")
@allure.story("Departure Time Window Filtering Validation")
def test_departure_time_filter(driver, data):
    logger.info("STARTING EXECUTION: Test 2 - Departure Time Filter Validation")
    search_for_trains(driver)

    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    results_page.apply_time_filter(data['TimeFilterLabel'])
    assert results_page.verify_departure_times_in_range(data['StartHour'], data['EndHour'])
    logger.info("SUCCESS: Test 2 Passed.")

# TEST 3: DEPARTURE STATION FILTER
@pytest.mark.parametrize("data", station_filter_data)
@allure.feature("Positive Testing")
@allure.story("Departure Station Specific Filter Validation")
def test_departure_station_filter(driver, data):

    logger.info("STARTING EXECUTION: Test 3 - Departure Station Filter Validation")
    search_for_trains(driver)

    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    results_page.apply_station_filter(data['StationFilterLabel'])
    assert results_page.verify_departure_station_code(data['StationExpectedCode'])
    logger.info("SUCCESS: Test 3 Passed.")

# TEST 4: SORT BY DEPARTURE TIME
@pytest.mark.parametrize("data", dep_sort_data)
@allure.feature("Positive Testing")
@allure.story("Sorting Validation: Departure Earliest to Late")
def test_sort_by_departure_time(driver, data):

    logger.info("STARTING EXECUTION: Test 4 - Sort by Departure Time Chronology")
    search_for_trains(driver)

    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    results_page.select_sort_option(data['SortLabelKey'])
    assert results_page.verify_time_sorting(check_departure=True, ascending=True)
    logger.info("SUCCESS: Test 4 Passed.")

# TEST 5: SORT BY ARRIVAL TIME
@pytest.mark.parametrize("data", arr_sort_data)
@allure.feature("Positive Testing")
@allure.story("Sorting Validation: Arrival Late to Earliest")
def test_sort_by_arrival_time(driver, data):

    logger.info("STARTING EXECUTION: Test 5 - Sort by Arrival Time Chronology (Late to Earliest)")
    search_for_trains(driver)
    results_page = ResultsPage(driver)

    assert results_page.verify_results_loaded(), "Train results page failed to load!"
    results_page.select_sort_option(data['SortLabelKey'])
    assert results_page.verify_time_sorting(check_departure=False, ascending=True)

# NEGATIVE TESTS

# TEST NEG 1: BOOKING WINDOW LIMIT
@pytest.mark.parametrize("data", invalid_date_data)
@allure.feature("Validation Testing")
@allure.story("Negative Boundary: Date Outside Booking Window")
def test_booking_window_limit(driver, data):

    logger.info("STARTING EXECUTION: Test Neg 1 - Booking Window Limit")
    logger.info(f"Testing route: {data['Source']} to {data['Destination']} on {data['TravelMonth']} {data['TravelDay']}")

    homepage = HomePage(driver)
    results_page = ResultsPage(driver)

    homepage.open_goibibo()
    homepage.popup_close()
    homepage.train_data_for_csv(data)

    with allure.step("Verify booking not open error message"):
        assert results_page.is_booking_not_open_error_shown(), \
            "Expected booking not open error but it was not displayed"

    results_page.take_screenshot("neg1_booking_window_limit_passed")
    logger.info("SUCCESS: Test Neg 1 Passed.")


# TEST NEG 2: NO DIRECT TRAINS FOUND
@allure.feature("Validation Testing")
@allure.story("Negative Boundary: Absolute Empty Search Results Route")
def test_absolute_empty_search_route(driver):

    logger.info("STARTING EXECUTION: Test Neg 2 - Empty Route Validation")
    data = random.choice(no_trains_data)
    logger.info(f"Testing random route: {data['Source']} to {data['Destination']}")

    homepage = HomePage(driver)
    results_page = ResultsPage(driver)

    homepage.open_goibibo()
    homepage.popup_close()
    homepage.train_data_for_csv(data)

    with allure.step("Verify no direct trains error message"):
        assert results_page.is_no_trains_error_shown(), \
            f"Expected no trains error for {data['srcname']} to {data['destname']} but it was not displayed"

    results_page.take_screenshot("neg2_empty_route_passed")
    logger.info(f"SUCCESS: Test Neg 2 Passed for {data['srcname']} to {data['destname']}")
