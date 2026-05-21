import pytest
import time
from pages.homepage import HomePage
from pages.results_page import ResultsPage
from utils.logger import LogGen
from utils.csv_reader import CSVReader
import csv
import os
import random
import allure



logger = LogGen.loggen()

# Separate CSV files for each independent verification checkpoint
train_data = CSVReader.read_csv("search_trains.csv")
filter_data = CSVReader.read_csv("filter_class.csv") # Read your new filter data file
time_filter_data = CSVReader.read_csv("filter_time.csv")
station_filter_data = CSVReader.read_csv("filter_station.csv")
dep_sort_data = CSVReader.read_csv("sort_departure.csv")
arr_sort_data = CSVReader.read_csv("sort_arrival.csv")
invalid_date_data = CSVReader.read_csv("invalid_date.csv")
no_trains_data    = CSVReader.read_csv("no_trains.csv")


def search_for_trains(driver):
    homepage = HomePage(driver)
    homepage.open_goibibo()
    homepage.train_data_for_csv(train_data[0])




def read_single_row_csv(file_name):
    """Utility helper to pull data from separate CSV files safely"""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", file_name)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing expected CSV test data file at: {csv_path}")
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return next(reader)
# Function to read ONLY the Booking Window CSV



'''
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
''' # initial valid search test




# TEST 1: COACH CLASS FILTER

@allure.feature("Positive Testing")
@allure.story("Coach Class Filtering Validation")
def test_coach_class_filter(driver):
    logger.info("=================================================================")
    logger.info("STARTING EXECUTION: Test 1 - Coach Class Filter Validation")
    logger.info("=================================================================")

    # 1. This handles the entire search flow using search_trains.csv[0]
    search_for_trains(driver)

    results_page = ResultsPage(driver)

    # 2. Verify results dashboard loaded successfully
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    # Extract our filter target dictionary
    current_filter = filter_data[0]

    # 3. Apply Left Sidebar Filter using the separate file's data
    results_page.apply_dynamic_class_filter(current_filter['ClassFilterLabel'])
    time.sleep(2)

    # 4. Assert and Verify
    is_verified = results_page.verify_class_present_in_results(current_filter['ClassExpectedCode'])
    assert is_verified, f"Filter validation failed! Active listings did not map to {current_filter['ClassExpectedCode']}."

    logger.info("SUCCESS: Test 1 - Coach Class Filter verified successfully.")


# TEST 2: DEPARTURE TIME FILTER

@allure.feature("Positive Testing")
@allure.story("Departure Time Window Filtering Validation")
def test_departure_time_filter(driver):
    logger.info("STARTING EXECUTION: Test 2 - Departure Time Filter Validation")
    search_for_trains(driver)
    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    current_filter = time_filter_data[0]
    results_page.apply_time_filter(current_filter['TimeFilterLabel'])
    assert results_page.verify_departure_times_in_range(current_filter['StartHour'], current_filter['EndHour'])
    logger.info("SUCCESS: Test 2 Passed.")


# TEST 3: DEPARTURE STATION FILTER

@allure.feature("Positive Testing")
@allure.story("Departure Station Specific Filter Validation")
def test_departure_station_filter(driver):
    logger.info("STARTING EXECUTION: Test 3 - Departure Station Filter Validation")
    search_for_trains(driver)
    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    current_filter = station_filter_data[0]
    results_page.apply_station_filter(current_filter['StationFilterLabel'])
    assert results_page.verify_departure_station_code(current_filter['StationExpectedCode'])
    logger.info("SUCCESS: Test 3 Passed.")


# TEST 4: SORT BY DEPARTURE TIME

@allure.feature("Positive Testing")
@allure.story("Sorting Validation: Departure Earliest to Late")
def test_sort_by_departure_time(driver):
    logger.info("STARTING EXECUTION: Test 4 - Sort by Departure Time Chronology")
    search_for_trains(driver)
    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    current_sort = dep_sort_data[0]
    results_page.select_sort_option(current_sort['SortLabelKey'])
    assert results_page.verify_time_sorting(check_departure=True)
    logger.info("SUCCESS: Test 4 Passed.")


# TEST 5: SORT BY ARRIVAL TIME

@allure.feature("Positive Testing")
@allure.story("Sorting Validation: Arrival Late to Earliest")
def test_sort_by_arrival_time(driver):
    logger.info("STARTING EXECUTION: Test 5 - Sort by Arrival Time Chronology (Late to Earliest)")
    search_for_trains(driver)
    results_page = ResultsPage(driver)
    assert results_page.verify_results_loaded(), "Train results page failed to load!"

    # Make sure your excel / test data dictionary matches 'Arrival'
    current_sort = arr_sort_data[0]
    results_page.select_sort_option(current_sort['SortLabelKey'])

    # Pass ascending=False to trigger reverse sorting assertion rule
    assert results_page.verify_time_sorting(check_departure=False, ascending=True)




# TEST NEG 1: BOOKING WINDOW LIMIT

@allure.feature("Validation Testing")
@allure.story("Negative Boundary: Date Outside Booking Window")
def test_booking_window_limit(driver):
    logger.info("STARTING EXECUTION: Test Neg 1 - Booking Window Limit")

    data = invalid_date_data[0]
    logger.info(f"Testing route: {data['Source']} to {data['Destination']} on {data['TravelMonth']} {data['TravelDay']}")

    homepage = HomePage(driver)
    results_page = ResultsPage(driver)

    homepage.open_goibibo()
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
    homepage.train_data_for_csv(data)

    with allure.step("Verify no direct trains error message"):
        assert results_page.is_no_trains_error_shown(), \
            f"Expected no trains error for {data['Source']} to {data['Destination']} but it was not displayed"

    results_page.take_screenshot("neg2_empty_route_passed")
    logger.info(f"SUCCESS: Test Neg 2 Passed for {data['Source']} to {data['Destination']}")