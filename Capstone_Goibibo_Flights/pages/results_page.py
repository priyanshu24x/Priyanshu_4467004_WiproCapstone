from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from pages.basepage import BasePage
import time
import allure
import re
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import LogGen

logger = LogGen.loggen()


class ResultsPage(BasePage):
    # Consolidated your headers with the dynamic filters
    RESULTS_HEADER = (By.XPATH,
                      "//p[contains(@class, 'paleGreyText') and contains(text(), 'trains on or near this route')] | //div[contains(text(), 'We have found')]")
    SHOW_AVAILABLE_ONLY_CHECKBOX = (By.XPATH, "//label[@for='Show available only0']")
    BOOKING_NOT_OPEN_MSG = (By.XPATH,
                            "//p[contains(@class,'paleGreyText') and contains(text(),\"Bookings aren't open\")]")
    NO_TRAINS_MSG = (By.XPATH,
                     "//p[contains(@class,'paleGreyText') and contains(text(),'No direct running trains found')]")
    TIME_FILTER_LABEL_XPATH = "//label[contains(., '{0}')]"
    STATION_FILTER_LABEL_XPATH = "//label[contains(text(), '{0}')] | //label[@for[contains(., '{0}')]]"
    # Targets the exact bold station uppercase text node sitting directly next to the parenthesis description
    CARD_STATION_CODES = (By.XPATH, "//div[contains(@class, 'appendTop16')]/div[contains(@class, 'makeFlex')][1]//p[contains(@class, 'rubikSemiBold')]")

    SORT_DROPDOWN_TRIGGER = (By.XPATH, "//div[contains(@class, 'srtdBy__fUlis')]")

    # Updated to target the parent list item directly for maximum reliability
    SORT_OPTION_XPATH = "//li[contains(@class, 'srtdBy__ddCntItm')]//span[text()='{0}']/ancestor::li"

    # Matches any paragraph tag containing a colon (e.g. 12:08) with the exact font classes
    TRAIN_TIME_NODES = (By.XPATH,
                        "//p[contains(@class, 'font16') and contains(@class, 'rubikMedium') and contains(text(), ':')]")

    # ZERO RESULTS EMPTY STATE TEST LOCATOR
    EMPTY_RESULTS_MESSAGE_BAN = (By.XPATH, "//*[contains(text(), 'No direct running trains found')]")

    @allure.step("Verify Search Results Loaded")
    def verify_results_loaded(self):
        is_header_visible = self.is_visible(self.RESULTS_HEADER)
        current_url = self.driver.current_url
        is_url_correct = "/trains/" in current_url or "search" in current_url
        self.take_screenshot("search_results_page_loaded")
        return is_header_visible and is_url_correct

    @allure.step("Apply 'Show available only' Filter")
    def apply_available_only_filter(self):
        logger.info("Engaging 'Show available only' filter to hide waitlisted blocks...")
        filter_box = self.wait.until(EC.element_to_be_clickable(self.SHOW_AVAILABLE_ONLY_CHECKBOX))
        filter_box.click()
        time.sleep(1.5)
        self.take_screenshot("available_only_filter_applied")

    @allure.step("Apply Dynamic Class Sidebar Filter: {class_filter}")
    def apply_dynamic_class_filter(self, class_filter):
        logger.info(f"Applying left sidebar filter: '{class_filter}'...")
        dynamic_locator = (By.XPATH, f"//label[contains(text(), '{class_filter}')]")
        el = self.wait.until(EC.element_to_be_clickable(dynamic_locator))
        el.click()
        time.sleep(1.5)
        self.take_screenshot(f"{class_filter}_filter_applied")

    @allure.step("Scan and Select Train meeting threshold: >= {min_seats} seats")
    def select_first_valid_train(self, class_filter, min_seats):
        logger.info(f"Scanning active train cards for '{class_filter}' availability >= {min_seats}...")

        # 1. Finds the seat item block (li) that contains our targeted class filter (e.g., '2A')
        # 2. Selects the availability paragraph within that exact block containing 'AVL' or 'AVAILABLE'
        availability_blocks_xpath = (
            f"//li[contains(@class, 'TrainCard_trnCrd__seatsLstItm__')][descendant::p[text()='{class_filter}']]"
            f"//p[contains(text(), 'AVL') or contains(text(), 'AVAILABLE')]"
        )

        try:
            blocks = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, availability_blocks_xpath)))
        except TimeoutException:
            logger.error("Timed out waiting for train availability nodes to appear. Check filters or DOM structure.")
            self.take_screenshot("train_blocks_not_found")
            raise

        for block in blocks:
            text = block.text.strip()  # This will read strings like "AVL 100"
            logger.info(f"Inspecting block text: '{text}'")

            numbers = re.findall(r'\d+', text)

            if numbers:
                available_count = int(numbers[0])
                logger.info(f"Checking train card: Found {available_count} seats available.")

                if available_count >= int(min_seats):
                    logger.info(f"Threshold met! Selecting train with {available_count} seats.")

                    # We want to click the interactive parent box container (the <li> card button wrapper)
                    clickable_card = block.find_element(By.XPATH,
                                                        "./ancestor::li[contains(@class, 'TrainCard_trnCrd__seatsLstItm__')]")

                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_card)
                    time.sleep(0.5)

                    # Using JavaScript click here as well since train card listings frequently suffer from overlay interceptions
                    self.driver.execute_script("arguments[0].click();", clickable_card)

                    self.take_screenshot(f"valid_train_{class_filter}_selected")
                    return True
            else:
                logger.warning(f"Could not parse digits from string text node: {text}")

        raise Exception(f"CRITICAL: No trains found with availability >= {min_seats} after applying filters.")

    # TEST 1 METHODS: CLASS FILTERING
    @allure.step("Verify all visible train cards contain class: {expected_code}")
    def verify_class_present_in_results(self, expected_code):
        logger.info(f"Verifying that visible train cards show option: {expected_code}")

        # Scans the active text layout nodes of the top train listings
        try:
            self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'TrainCard_trnCrd__')]")))
            card_text_blocks = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'TrainCard_trnCrd__')]")

            # Verify the first 3 cards to keep testing performant but precise
            for idx, card in enumerate(card_text_blocks[:3]):
                card_content = card.text
                assert expected_code in card_content, f"CRITICAL: Expected class {expected_code} not found on train card {idx + 1}!"
                logger.info(f"Card {idx + 1} successfully verified for class {expected_code}.")

            return True
        except Exception as e:
            logger.error(f"Class verification failed on results block: {e}")
            self.take_screenshot("class_verification_failure")
            return False

    # TEST 2 METHODS: TIME FILTERING
    @allure.step("Apply Left Sidebar Time Filter: {time_label}")
    def apply_time_filter(self, time_label):
        logger.info(f"Applying time filter checkbox matching: '{time_label}'")
        dynamic_xpath = self.TIME_FILTER_LABEL_XPATH.format(time_label)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, dynamic_xpath)))
        # Execute via JavaScript to bypass layout element click interception overrides
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(2.5)
        self.take_screenshot("time_filter_applied")

    @allure.step("Verify departure times fall within specified hour boundaries")
    def verify_departure_times_in_range(self, start_hour, end_hour):
        logger.info(f"Verifying departure hours range window: {start_hour} to {end_hour}")
        try:
            time.sleep(2.5)  # Let filters apply visually

            time_elements = self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_TIME_NODES))

            parsed_departure_hours = []
            import re

            # Slice [0::2] immediately grabs only the Departure elements from the DOM
            for element in time_elements[0::2][:4]:
                raw_text = element.text.strip().lower()
                time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', raw_text)

                if time_match:
                    h = int(time_match.group(1))
                    am_pm = time_match.group(3)

                    if am_pm:
                        if am_pm == "pm" and h != 12:
                            h += 12
                        elif am_pm == "am" and h == 12:
                            h = 0
                    parsed_departure_hours.append(h)

            logger.info(f"Extracted departure hours for validation: {parsed_departure_hours}")
            assert len(parsed_departure_hours) > 0, "No departure times found to validate!"

            for h in parsed_departure_hours:
                # Validate the hour falls between the requested integer parameters
                assert int(start_hour) <= h < int(end_hour), f"Time {h} outside window {start_hour}-{end_hour}"

            return True
        except Exception as e:
            logger.error(f"Time window validation failed: {e}")
            return False

    # TEST 3 METHODS: STATION FILTERING
    @allure.step("Apply Left Sidebar Station Filter: {station_name}")
    def apply_station_filter(self, station_name):
        logger.info(f"Applying station filter checkbox matching: '{station_name}'")
        dynamic_xpath = self.STATION_FILTER_LABEL_XPATH.format(station_name)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, dynamic_xpath)))
        # JavaScript execution avoids standard pointer action blocking
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(2.5)
        self.take_screenshot("station_filter_applied")

    @allure.step("Verify train departure stations match: {expected_code}")
    def verify_departure_station_code(self, expected_code):
        logger.info(f"Verifying departure station matches: '{expected_code}'")
        try:
            station_elements = self.wait.until(EC.presence_of_all_elements_located(self.CARD_STATION_CODES))
            for idx, element in enumerate(station_elements[:3]):
                actual_code = element.text.strip()
                logger.info(f"Card {idx + 1} parsed station tag code: '{actual_code}'")
                assert actual_code == expected_code, f"Station code mismatch! Expected {expected_code}, got {actual_code}"
            return True
        except Exception as e:
            logger.error(f"Station validation failed: {e}")
            return False

    # TESTS 4 & 5 METHODS: SORTING DRIVERS
    @allure.step("Selectsort option criteria parameter from dropdown view")
    def select_sort_option(self, option_text):
        logger.info(f"Opening sort dropdown menu to select: '{option_text}'")
        try:
            # 1. Open the dropdown menu panel securely
            dropdown_trigger = self.wait.until(EC.element_to_be_clickable(self.SORT_DROPDOWN_TRIGGER))
            self.driver.execute_script("arguments[0].click();", dropdown_trigger)
            time.sleep(1)  # Small pause to let the dropdown list DOM fully expand

            # 2. Format the dynamic XPath with your exact target text string
            formatted_xpath = self.SORT_OPTION_XPATH.format(option_text)
            logger.info(f"Targeting formatted option XPath structure: {formatted_xpath}")

            # 3. Locate the targeted sorting list option element
            target_option = self.wait.until(EC.presence_of_element_located((By.XPATH, formatted_xpath)))

            # 4. Use JavaScript to force the click choice selection directly
            self.driver.execute_script("arguments[0].click();", target_option)
            logger.info(f"Successfully triggered selection choice parameter for: '{option_text}'")

            # 5. Let the page finish re-shuffling the train cards dynamically
            time.sleep(2.5)
        except Exception as e:
            logger.error(f"Failed to open or click option choice inside dropdown component view: {e}")
            raise e

    @allure.step("Verify chronology order of sequence timeline")
    def verify_time_sorting(self, check_departure=True, ascending=True):
        logger.info(f"Validating time sequence. Target departure? {check_departure} | Expect Ascending? {ascending}")
        try:
            time.sleep(2.5)  # Let dynamic re-sorting render

            # Grab EVERY time element on the page
            time_elements = self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_TIME_NODES))

            all_parsed_minutes = []
            import re
            for element in time_elements:
                raw_text = element.text.strip().lower()
                time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', raw_text)

                if time_match:
                    h = int(time_match.group(1))        # just to match the time
                    m = int(time_match.group(2))
                    am_pm = time_match.group(3)

                    if am_pm:
                        if am_pm == "pm" and h != 12:
                            h += 12
                        elif am_pm == "am" and h == 12:
                            h = 0
                    all_parsed_minutes.append(h * 60 + m)

            departures = all_parsed_minutes[0::2]
            arrivals = all_parsed_minutes[1::2]

            target_list = departures if check_departure else arrivals
            target_list = target_list[:4]  # Only evaluate the top 4 cards

            logger.info(f"Generated timeline list minutes: {target_list}")
            assert len(target_list) > 0, "CRITICAL ERROR: No valid times parsed!"

            if ascending:
                assert target_list == sorted(target_list), f"Out of ascending order: {target_list}"
            else:
                assert target_list == sorted(target_list, reverse=True), f"Out of descending order: {target_list}"

            return True
        except Exception as e:
            logger.error(f"Sorting sequence verification encountered failures: {e}")
            return False

    @allure.step("Extract explicit zero-results empty state notice text")
    def get_empty_results_message_text(self):
        try:
            import selenium.webdriver.support.ui as ui
            short_wait = ui.WebDriverWait(self.driver, 6)
            element = short_wait.until(EC.visibility_of_element_located(self.EMPTY_RESULTS_MESSAGE_BAN))
            text = element.text.strip()
            logger.info(f"Captured zero-results text block notice: '{text}'")
            return text
        except Exception as e:
            logger.error(f"Could not locate zero-results text block notification: {e}")
            return ""

    # TEST 6  NEG METHODS: BOOKING UNAVAILABLE
    def is_booking_not_open_error_shown(self):
        logger.info("Checking for booking not open error message")
        try:
            time.sleep(3)  # wait for page to settle after search
            # Try multiple locator approaches
            locator = (By.XPATH,
                       "//p[contains(text(),\"Bookings aren't open\")] | "
                       "//p[contains(text(),'Bookings are not open')] | "
                       "//*[contains(text(),'booking window opens')]")
            self.wait.until(EC.presence_of_element_located(locator))
            logger.info("Booking not open error message found")
            self.take_screenshot("booking_not_open_confirmed")
            return True
        except Exception as e:
            logger.error(f"Booking error message not found: {e}")
            self.take_screenshot("booking_error_not_found")
            return False

    # TEST 7 NEG METHODS: TRAINS NOT AVAILABLE
    def is_no_trains_error_shown(self):
        logger.info("Checking for no trains found error message")
        try:
            self.wait.until(EC.visibility_of_element_located(self.NO_TRAINS_MSG))
            logger.info("No trains error message visible")
            self.take_screenshot("no_trains_confirmed")
            return True
        except Exception as e:
            logger.error(f"No trains message not found: {e}")
            self.take_screenshot("no_trains_error_not_found")
            return False
