# IMPORTS FOR RESULT PAGE
from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from pages.basepage import BasePage

import allure
import re
from selenium.webdriver.support import expected_conditions as EC, ui
from utils.logger import LogGen

logger = LogGen.loggen()


class ResultsPage(BasePage):

    # LOCATORS FOR HEADER AND AVAILABLE ONLY FILTER
    RESULTS_HEADER = (By.XPATH,"//p[contains(@class, 'paleGreyText') and contains(text(), 'trains on or near this route')] | //div[contains(text(), 'We have found')]")
    SHOW_AVAILABLE_ONLY_CHECKBOX = (By.XPATH, "//label[@for='Show available only0']")

    # LOCATORS FOR CAPTURING TEXT ELEMENTS OF TRAINS AND STATIONS
    TRAIN_TIME_NODES = (By.XPATH,
                        "//p[@class='font16 rubikMedium blackText' and contains(text(),':')]")
    TRAIN_STATION_CODES = (By.XPATH, "//div[contains(@class, 'appendTop16')]/div[contains(@class, 'makeFlex')][1]//p[contains(@class, 'rubikSemiBold')]")



    # LOCATORS FOR STRINGS
    SORT_OPTION_XPATH = "//li[contains(@class, 'srtdBy__ddCntItm')]//span[text()='{0}']/ancestor::li"
    TIME_FILTER_LABEL_XPATH = "//label[contains(., '{0}')]"
    STATION_FILTER_LABEL_XPATH = "//label[contains(text(), '{0}')] | //label[@for[contains(., '{0}')]]"

    TRAIN_CARD_LIST = (By.XPATH,
                       "//li[contains(@class, 'TrainCard_trnCrd__seatsLstItm__')]//p[@class='font16 blackText2 rubikMedium']")
    # LOCATOR FOR SORT OPTIONS
    SORT_DROPDOWN_TRIGGER = (By.XPATH, "//div[contains(@class, 'srtdBy__fUlis')]")

    # LOCATORS FOR ERROR MESSAGES
    BOOKING_NOT_OPEN_MSG = (By.XPATH,
                            "//*[contains(text(), \"Bookings aren't open\") or "
                            "contains(text(), 'Bookings are not open') or "
                            "contains(text(), 'booking window') or "
                            "contains(text(), 'advance booking')]"
                            )
    NO_TRAINS_MSG = (By.XPATH,"//p[contains(@class,'paleGreyText') and contains(text(),'No direct running trains found')]")
    EMPTY_RESULTS_MESSAGE_BAN = (By.XPATH, "//*[contains(text(), 'No direct running trains found')]")

    # VERIFY THE RESULTS
    @allure.step("Verify Search Results Loaded")
    def verify_results_loaded(self):

        is_header_visible = self.is_visible(self.RESULTS_HEADER)
        current_url = self.driver.current_url
        is_url_correct = "/trains/" in current_url or "search" in current_url

        self.take_screenshot("search_results_page_loaded")
        return is_header_visible and is_url_correct

    # FILTER TO GET ONLY AVAILABLE TRAINS
    @allure.step("Apply 'Show available only' Filter")
    def apply_available_only_filter(self):

        logger.info("Engaging 'Show available only' filter to hide waitlisted blocks...")
        filter_box = self.wait.until(EC.element_to_be_clickable(self.SHOW_AVAILABLE_ONLY_CHECKBOX))
        filter_box.click()

        self.take_screenshot("available_only_filter_applied")

    # GET THE TRAIN COUNT TO VERIFY IT'S NOT ZERO
    def get_visible_train_count(self):

        try:
            self.wait.until(lambda driver: len(driver.find_elements(*self.TRAIN_CARD_LIST)) >0)
            cards = self.driver.find_elements(*self.TRAIN_CARD_LIST)
            visible_card = [card for card in cards if card.is_displayed()]

            return len(visible_card)
        except Exception:
            return 0

    # FINDING THE FIRST TRAIN AVAILABLE AND CLICKING IT
    @allure.step("Scan and Select Train meeting threshold: >= {min_seats} seats")
    def select_first_valid_train(self, class_filter, min_seats):

        logger.info(f"Scanning active train cards for '{class_filter}' availability >= {min_seats}...")

        availability_blocks_xpath = (f"//li[contains(@class, 'TrainCard_trnCrd__seatsLstItm__')][descendant::p[text()='{class_filter}']]//p[contains(text(), 'AVL') or contains(text(), 'AVAILABLE')]")

        # FINDING THE TRAINS
        try:
            blocks = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, availability_blocks_xpath)))

        except TimeoutException:
            logger.error("Timed out waiting for train availability nodes to appear. Check filters or DOM structure.")
            self.take_screenshot("train_blocks_not_found")
            raise

        for block in blocks:
            try:
                text = block.text.strip()  # This will read strings like "AVL 100"
                logger.info(f"Inspecting block text: '{text}'")
                numbers = re.findall(r'\d+', text)

                # FIND FIRST TRAIN CARD AND SELECT IT

                if numbers:
                    available_count = int(numbers[0])
                    logger.info(f"Checking train card: Found {available_count} seats available.")

                    if available_count >= int(min_seats):
                        logger.info(f"Threshold met! Selecting train with {available_count} seats.")
                        clickable_card = block.find_element(By.XPATH, "./ancestor::li[contains(@class, 'TrainCard_trnCrd__seatsLstItm__')]")

                        self.wait.until(EC.element_to_be_clickable(clickable_card))
                        clickable_card.click()

                        self.take_screenshot(f"valid_train_{class_filter}_selected")
                        return True
                else:
                    logger.warning(f"Could not parse digits from string text node: {text}")

            except StaleElementReferenceException:
                logger.warning(
                    "Encountered stale element reference during loop processing. The page layout updated mid-execution.")
                continue

        raise Exception(f"CRITICAL: No trains found with availability >= {min_seats} after applying filters.")

    # APPLY THE CLASS FILTER AS GIVEN BY THE USER FOR TEST CASE 1
    @allure.step("Apply Dynamic Class Sidebar Filter: {class_filter}")
    def apply_dynamic_class_filter(self, class_filter):

        logger.info(f"Applying left sidebar filter: '{class_filter}'...")
        dynamic_locator = (By.XPATH, f"//label[contains(text(), '{class_filter}')]")

        element = self.wait.until(EC.presence_of_element_located(dynamic_locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)
        self.take_screenshot(f"{class_filter}_filter_applied")

    # VERIFYING ALL TRAINS ARE ACCORDING TO THE APPLIED CLASS FILTER FOR TEST CASE 1
    @allure.step("Verify all visible train cards contain class: {expected_code}")
    def verify_class_present_in_results(self, expected_code):
        logger.info(f"Verifying that visible train cards show option: {expected_code}")
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_CARD_LIST))
            for idx, el in enumerate(elements[:3]):
                try:
                    text = el.text.strip()
                except StaleElementReferenceException:
                    continue
                assert text == expected_code, f"Expected {expected_code} but got '{text}' on card {idx + 1}"
                logger.info(f"Card {idx + 1} verified: {text}")
            return True
        except Exception as e:
            logger.error(f"Class verification failed: {e}")
            self.take_screenshot("class_verification_failure")
            return False

    # APPLY THE TIME FILTER AS GIVEN BY THE USER FOR TEST CASE 2
    @allure.step("Apply Left Sidebar Time Filter: {time_label}")
    def apply_time_filter(self, time_label):

        logger.info(f"Applying time filter checkbox matching: '{time_label}'")
        dynamic_xpath = self.TIME_FILTER_LABEL_XPATH.format(time_label)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, dynamic_xpath)))

        self.driver.execute_script("arguments[0].click();", element)
        self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_TIME_NODES))
        self.take_screenshot("time_filter_applied")

    # VERIFYING ALL TRAINS ARE ACCORDING TO THE APPLIED TIME FILTER FOR TEST CASE 2
    @allure.step("Verify departure times fall within specified hour boundaries")
    def verify_departure_times_in_range(self, start_hour, end_hour):

        logger.info(f"Verifying departure hours range window: {start_hour} to {end_hour}")
        try:
            time_elements = self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_TIME_NODES))
            parsed_departure_hours = []

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
                assert int(start_hour) <= h < int(end_hour), f"Time {h} outside window {start_hour}-{end_hour}"

            return True
        except Exception as e:
            logger.error(f"Time window validation failed: {e}")
            return False

    # APPLY THE STATION FILTER AS GIVEN BY THE USER FOR TEST CASE 3
    @allure.step("Apply Left Sidebar Station Filter: {station_name}")
    def apply_station_filter(self, station_name):

        logger.info(f"Applying station filter checkbox matching: '{station_name}'")
        dynamic_xpath = self.STATION_FILTER_LABEL_XPATH.format(station_name)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, dynamic_xpath)))

        self.driver.execute_script("arguments[0].click();", element)
        self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_STATION_CODES))
        self.take_screenshot("station_filter_applied")

    # VERIFYING ALL TRAINS ARE ACCORDING TO THE APPLIED STATION FILTER FOR TEST CASE 3
    @allure.step("Verify train departure stations match: {expected_code}")
    def verify_departure_station_code(self, expected_code):

        logger.info(f"Verifying departure station matches: '{expected_code}'")
        try:
            station_elements = self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_STATION_CODES))

            for idx, element in enumerate(station_elements[:3]):
                actual_code = element.text.strip()
                logger.info(f"Card {idx + 1} parsed station tag code: '{actual_code}'")

                assert actual_code == expected_code, f"Station code mismatch! Expected {expected_code}, got {actual_code}"
            return True

        except Exception as e:
            logger.error(f"Station validation failed: {e}")
            return False

    # SELECTING THE SORT OPTION THAT USER SELECTED FOR TEST CASES 4 AND 5
    @allure.step("Selectsort option criteria parameter from dropdown view")
    def select_sort_option(self, option_text):

        logger.info(f"Opening sort dropdown menu to select: '{option_text}'")
        try:
            dropdown_trigger = self.wait.until(EC.element_to_be_clickable(self.SORT_DROPDOWN_TRIGGER))

            self.driver.execute_script("arguments[0].click();", dropdown_trigger)
            self.wait.until(EC.visibility_of_element_located((By.XPATH, self.SORT_OPTION_XPATH.format(option_text))))

            formatted_xpath = self.SORT_OPTION_XPATH.format(option_text)
            logger.info(f"Targeting formatted option XPath structure: {formatted_xpath}")
            target_option = self.wait.until(EC.presence_of_element_located((By.XPATH, formatted_xpath)))

            self.driver.execute_script("arguments[0].click();", target_option)
            logger.info(f"Successfully triggered selection choice parameter for: '{option_text}'")

            self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_TIME_NODES))

        except Exception as e:
            logger.error(f"Failed to open or click option choice inside dropdown component view: {e}")
            raise e

    # VERIFYING THE TIME OF TRAINS FOR TEST CASES 4 AND 5
    @allure.step("Verify chronology order of sequence timeline")
    def verify_time_sorting(self, check_departure=True, ascending=True):

        self.wait.until(EC.staleness_of(
            self.driver.find_elements(*self.TRAIN_TIME_NODES)[0]
        ))

        logger.info(f"Validating time sequence. Target departure? {check_departure} | Expect Ascending? {ascending}")
        try:
            self.wait.until(EC.presence_of_all_elements_located(self.TRAIN_TIME_NODES))
            all_parsed_minutes = []

            for element in self.driver.find_elements(*self.TRAIN_TIME_NODES):
                try:
                    raw_text = element.text.strip().lower()
                except StaleElementReferenceException:
                    continue

                time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', raw_text)

                if time_match:
                    h = int(time_match.group(1))
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

            target_list = (departures if check_departure else arrivals)[:4]

            logger.info(f"Generated timeline list minutes: {target_list}")
            assert len(target_list) > 0, "CRITICAL ERROR: No valid times parsed!"

            if ascending:
                assert target_list == sorted(target_list), f"Out of ascending order: {target_list}"
                logger.info(f"Ascending sort verified: {target_list}")
            else:
                assert target_list == sorted(target_list, reverse=True), f"Out of descending order: {target_list}"
                logger.info(f"Descending sort verified: {target_list}")

            return True
        except Exception as e:
            logger.error(f"Sorting sequence verification encountered failures: {e}")
            return False

    # GIVING A DATE TOO FAR FOR BOOKING FOR NEGATIVE TEST CASE 1
    def is_booking_not_open_error_shown(self):

        logger.info("Checking for booking not open error message")
        try:
            # locator = (By.XPATH, "//p[contains(text(),\"Bookings aren't open\")] | //p[contains(text(),'Bookings are not open')] | //*[contains(text(),'booking window opens')]")
            self.wait.until(EC.visibility_of_element_located(self.BOOKING_NOT_OPEN_MSG))

            logger.info("Booking not open error message found")
            self.take_screenshot("booking_not_open_confirmed")
            return True

        except Exception as e:
            logger.error(f"Booking error message not found: {e}")
            self.take_screenshot("booking_error_not_found")

            return False

    # GIVING TWO STATIONS WITH UNAVAILABLE ROUTES FOR TEST CASE 2
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
