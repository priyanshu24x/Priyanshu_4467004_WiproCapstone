# IMPORTS FOR END TO END TESTS
import pytest
import allure
from selenium.webdriver.support import expected_conditions as EC
from pages.homepage import HomePage
from pages.results_page import ResultsPage
from pages.details_page import DetailsPage
from pages.payment_page import PaymentPage
from utils.logger import LogGen
from utils.excel_reader import ExcelReader

logger = LogGen.loggen()

# OPENING THE EXCEL FILE
FILE_NAME = "booking_data.xlsx"

train_data = ExcelReader.read_excel(FILE_NAME, "TrainData")
filter_data = ExcelReader.read_excel(FILE_NAME, "FilterPreferences")
passenger_data = ExcelReader.read_excel(FILE_NAME, "PassengerDetails")
card_data = ExcelReader.read_excel(FILE_NAME, "PaymentDetails")
details_data = list(zip(train_data, filter_data, passenger_data, card_data))


@pytest.mark.regression
@pytest.mark.parametrize("train, filter, passenger, card", details_data)
@allure.epic("Train Reservation System")
@allure.feature("End-to-End Booking Paths")
@allure.story("Dynamic Spreadsheet Journey Processing")
@allure.title("Dynamic E2E Train Booking Routing Flow")
@allure.description("Validates search filters, traveler details, and payment terminal data binding.")
def test_complete_train_booking_flow(driver, train, filter, passenger, card):
    logger.info("=================================================================")
    logger.info(f"STARTING EXECUTION: Routing from {train['Source']} to {train['Destination']}")
    logger.info("=================================================================")

    # CALLING PAGE FUNCTIONS
    homepage = HomePage(driver)
    results_page = ResultsPage(driver)
    details_page = DetailsPage(driver)
    payment_page = PaymentPage(driver)

    # STEP 0: DATA FROM THE EXCEL
    with allure.step(f"Step 0: Extracting Data from Excel File"):
        # GETTING DATA FROM EXCEL AS VARIABLES OF TrainData
        source_station_code = train["Source"]
        destination_station_code = train["Destination"]
        travel_month = train["TravelMonth"]
        travel_day = train["TravelDay"]

        # GETTING DATA FROM EXCEL AS VARIABLES OF FilterPreferences
        class_filter = filter["ClassFilter"]
        min_seats = filter["MinAvailabilityThreshold"]

        # GETTING DATA FROM EXCEL AS VARIABLES OF PassengerDetails
        pass_name = passenger["FullName"]
        pass_age = passenger["Age"]
        pass_gender = passenger["Gender"]
        meal = passenger["MealOption"]
        pass_mobile = passenger["ContactMobile"]
        pass_email = passenger["ContactEmail"]
        pass_id = passenger["IRCTCID"]

        # GETTING DATA FROM EXCEL AS VARIABLES OF PaymentDetails
        card_no = card["CardNumber"]
        exp_month = card["ExpiryMonth"]
        exp_year = card["ExpiryYear"]
        cvv = card["CVV"]
        card_name = card["CardName"]

    # STEP 1: HOMEPAGE LOOKUPS & DESTINATION ROUTING
    with (allure.step(f"Step 1: Configure Routing on Homepage ({source_station_code} -> {destination_station_code})")):
        logger.info("Entering routing paths...")

        # OPENING HOMEPAGE AND CLOSING POPUP
        homepage.popup_close()

        # ENTER STATION CODE OF SOURCE CITY AND ASSERTING IT
        homepage.enter_source(source_station_code)
        assert source_station_code.lower() in homepage.get_selected_source_text().lower(),f"Source match failure! Expected: '{source_station_code}'but got {homepage.get_selected_source_text()}"

        # ENTER STATION CODE OF DESTINATION CITY AND ASSERTING IT
        homepage.enter_destination(destination_station_code)
        assert destination_station_code.lower() in homepage.get_selected_destination_text().lower(), f"Destination match failure! Expected: '{destination_station_code}'but got {homepage.get_selected_destination_text()}"

        logger.info(f"Extracting target dates from Excel matrix: {travel_month} {travel_day}")

        # ENTERING TRAVEL MONTH AND DATE AND FINDING IT IN THE CALENDER AND ASSERTING IT
        homepage.select_journey_date(travel_month, travel_day)

        logger.info("Submitting query parameters -> Dispatching to Results View.")

        # SEARCHING FOR TRAINS
        homepage.click_search()

    # STEP 2: SEARCH RESULTS LISTING VERIFICATION & CHOICE SELECTION
    with allure.step("Step 2: Validate Search Results and Select Train"):
        logger.info("Awaiting Results Dashboard Page Anchor stability...")

        # OPENING RESULTS PAGE AND CLOSING POPUP
        homepage.popup_close()

        # ASSERTING IF TRAINS HAVE LOADED AND ARE PRESENT
        assert results_page.verify_results_loaded(), "CRITICAL FAILURE: Train results view failed to render!"
        logger.info(f"Anchor and URL verified successfully! Current URL: {driver.current_url}")

        # APPLYING AVAILABLE ONLY FILTER AND THE OTHER GIVEN FILTER
        results_page.apply_available_only_filter()
        results_page.apply_dynamic_class_filter(class_filter)

        # COUNTING AND ASSERTING THAT THERE ARE TRAINS STILL PRESENT
        train_count = results_page.get_visible_train_count()
        assert train_count > 0, f"Mismatch! Found Zero trains matching the class filter{class_filter}"
        logger.info(f"Filters verified successfully! Train count: {train_count}")

        # SCAN THE TRAIN CARD LIST AND CLICK THE FIRST VALID OPTION MEETING YOUR TARGET SEATS
        results_page.select_first_valid_train(class_filter, min_seats)
        logger.info("Valid train selected! Redirecting to checkout dashboard details...")

    # STEP 3: TRAVELLER REGISTRATION AND DATA-ENTRY VALIDATION
    with allure.step("Step 3: Fill Passenger Registration and Contact Channels"):
        logger.info("Arrived at Checkout Details Form view. Attaching profile credentials...")

        homepage.popup_close()
        # ENTER AND VALIDATING IRCTC ID
        details_page.enter_irctc_id(pass_id)
        logger.info("IRCTC Username applied.")

        # FILLING THE PASSENGER DETAILS AS NAME, AGE, GENDER, PREFERRED MEAL OPTION
        logger.info("Opening Passenger Registration modal view...")
        details_page.fill_passenger_details(pass_name, pass_age, pass_gender, meal)
        assert details_page.is_passenger_added_successfully(pass_name),f"Registration Failure! Passenger '{pass_name}'was not successfully added to the checkout layout list."

        logger.info("Configuring contact channels and disabling default insurance flags...")

        # SCROLLING DOWN AND FINALISING DETAILS
        details_page.scroll_to_element()
        details_page.select_cancellation_addon()
        details_page.wait.until(EC.visibility_of_element_located(details_page.CONTACT_NUMBER_INPUT))

        # FILLING PASSENGER CONTACT AND EMAIL DETAILS
        details_page.fill_contact_information(pass_mobile, pass_email)

        details_page.wait.until(EC.element_to_be_clickable(details_page.PROCEED_TO_PAYMENT_BUTTON))

        # PROCEEDING TO PAYMENT PAGE
        details_page.click_proceed_to_payment()

    # STEP 4: PAYMENT GATEWAY PROCESSING
    with allure.step("Step 4: Verify Payment Gateway Landing and Input Card Details"):
            logger.info("Arrived at payment gateway page view. Extracting test card details from Sheet 4...")

            homepage.popup_close()

            payment_tab_visible = payment_page.wait.until(EC.element_to_be_clickable(payment_page.CREDIT_CARD_TAB))
            assert payment_tab_visible.is_displayed(), (
                f"Gateway Blockage! Payment terminal page layer failed to render. Current URL: {driver.current_url}"
            )
            logger.info("Payment terminal container verified. Extracting card profiles...")

            # CLEAN AND FORMAT MONTH DATA (ENSURES 2 DIGITS, LIKE TURNING '5' INTO '05')
            clean_expiry_month = str(int(float(exp_month))).zfill(2)

            # CLEAN AND FORMAT YEAR DATA
            raw_year = str(int(float(exp_year)))

            # FALLBACK: IF EXCEL HAS A 2-DIGIT YEAR (E.G., '30'), CONVERT IT TO 4-DIGITS ('2030')
            if len(raw_year) == 2:
                clean_expiry_year = f"20{raw_year}"
            else:
                clean_expiry_year = raw_year

            # SEND CLEAN DATA TO PAYMENT PAGE OBJECT
            payment_page.fill_card_details(card_no, clean_expiry_month, clean_expiry_year, cvv, card_name)
            logger.info("Card profile arrays typed. Evaluating field compliance...")
