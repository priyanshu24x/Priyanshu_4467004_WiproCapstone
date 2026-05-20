import pytest
import time
import allure
from pages.homepage import HomePage
from pages.results_page import ResultsPage
from pages.details_page import DetailsPage
from pages.payment_page import PaymentPage
from utils.logger import LogGen
from utils.excel_reader import ExcelReader

logger = LogGen.loggen()

# Load the dynamic journey route details from Sheet 1
FILE_NAME = "booking_data.xlsx"

train_data_list = ExcelReader.read_excel(FILE_NAME, "TrainData")

# DEBUG PRINT BLOCK
print("\n" + "="*50)
print(f"DEBUG: Collected data rows from Excel: {train_data_list}")
print("="*50 + "\n")

@pytest.mark.parametrize("data", train_data_list)
@allure.title("End-to-End Train Booking Journey")
@allure.description(
    "Validates search, filter selection, passenger details entry, and payment page routing dynamically via Excel.")
def test_complete_train_booking_flow(driver, data):
    logger.info("=================================================================")
    logger.info(f"STARTING EXECUTION: Routing from {data['Source']} to {data['Destination']}")
    logger.info("=================================================================")

    # Load filter constraints and seating preferences from Sheet 2
    filter_data = ExcelReader.read_excel("booking_data.xlsx", "FilterPreferences")[0]
    class_filter = filter_data['ClassFilter']
    min_threshold = filter_data['MinAvailabilityThreshold']

    homepage = HomePage(driver)
    results_page = ResultsPage(driver)
    details_page = DetailsPage(driver)
    payment_page = PaymentPage(driver)

    homepage.open_goibibo()

    # =========================================================================
    # STEP 1: HOMEPAGE LOOKUPS & DESTINATION ROUTING
    # =========================================================================
    logger.info("Entering routing paths...")

    homepage.enter_source(data['Source'])
    homepage.click_first_suggestion()

    homepage.enter_destination(data['Destination'])
    homepage.click_first_suggestion()

    # Simplified: Hardcoding the target date to isolate the Excel issue
    logger.info("Selecting hardcoded journey date (June 26)...")
    homepage.select_hardcoded_june_date()

    logger.info("Submitting query parameters -> Dispatching to Results View.")
    time.sleep(1)  # ⏳ Buffer to let the calendar UI fully close before clicking search
    homepage.click_search()

    # =========================================================================
    # STEP 2: SEARCH RESULTS LISTING VERIFICATION & CHOICE SELECTION
    # =========================================================================
    logger.info("Awaiting Results Dashboard Page Anchor stability...")

    assert results_page.verify_results_loaded(), "CRITICAL FAILURE: Train results view failed to render!"
    logger.info(f"Anchor and URL verified successfully! Current URL: {driver.current_url}")

    # Apply your optimization filters dynamically
    results_page.apply_available_only_filter()
    results_page.apply_dynamic_class_filter(class_filter)

    # Automatically scan the train card list and click the first valid option meeting your target seats
    results_page.select_first_valid_train(class_filter, min_threshold)
    logger.info("Valid train selected! Redirecting to checkout dashboard details...")

    # =========================================================================
    # STEP 3: TRAVELLER REGISTRATION AND DATA-ENTRY VALIDATION
    # =========================================================================
    logger.info("Arrived at Checkout Details Form view. Attaching profile credentials...")

    details_page.enter_irctc_id("priyanshu4902")
    logger.info("IRCTC Username applied.")

    logger.info("Opening Passenger Registration modal view...")
    details_page.fill_passenger_details(name="John Doe", age=32, gender="male")

    logger.info("Configuring contact channels and disabling default insurance flags...")
    details_page.wait_for_modal_to_settle()
    time.sleep(1)
    details_page.scroll_to_element()
    time.sleep(1)
    details_page.select_cancellation_addon()
    time.sleep(1)
    details_page.fill_contact_information(mobile="9019019015", email="automation_test@gmail.com")
    time.sleep(1.5)
    details_page.click_proceed_to_payment()

    # =========================================================================
    # STEP 4: GATEWAY LANDING & MOCK CARD DETAIL POPULATION
    # =========================================================================
    logger.info("Arrived at Final Secure Checkout Terminal Panel.")
    payment_page.navigate_to_credit_card_form()
    time.sleep(1)

    payment_page.fill_mock_card_details(card_no="1234567812345678", cvv="123")
    time.sleep(4)

    logger.info("=================================================================")
    logger.info("SUCCESS: Full Booking Flow Executed and Verified Flawlessly!")
    logger.info("=================================================================")