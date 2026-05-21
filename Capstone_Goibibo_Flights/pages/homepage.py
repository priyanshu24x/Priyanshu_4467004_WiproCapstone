# Contains structurally insulated locators and methods for Goibibo Train search forms.
import time
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.basepage import BasePage
from utils.logger import LogGen

logger = LogGen.loggen()


class HomePage(BasePage):
    SOURCE_CONTAINER = (By.XPATH, "//p[contains(@class, 'styles_FswFldHeading') and text()='From']")
    DESTINATION_CONTAINER = (By.XPATH, "//p[contains(@class, 'styles_FswFldHeading') and text()='To']")
    ACTIVE_INPUT = (By.XPATH, "//input[@type='text' or @role='combobox']")
    AUTO_SUGGEST_OPTIONS = (By.XPATH, "//div[contains(@class, 'styles_FswAutoCompItemDesc')] | //p[contains(@class, 'styles_FswAutoCompItemDescTitle')]")
    CALENDAR_NEXT_ARROW = (By.XPATH, "//span[contains(@class, 'styles_calNextArrow')]")
    TRAIN_SEARCH_BTN = (By.XPATH, "//span[contains(@class, 'styles_FswSearchCta') and text()='SEARCH TRAINS']")

    @allure.step("Navigate to Goibibo Trains Homepage")
    def open_goibibo(self):
        logger.info("Navigating to https://www.goibibo.com/trains/")
        self.driver.get("https://www.goibibo.com/trains/")
        self.driver.maximize_window()
        self.driver.execute_script("document.elementFromPoint(window.innerWidth/2, window.innerHeight/2).click();")
        time.sleep(1)
        self.take_screenshot("goibibo_homepage_loaded")

    @allure.step("Enter Source City: {city}")
    def enter_source(self, city):
        logger.info(f"Opening Source input view and typing: {city}")
        container = self.wait.until(EC.element_to_be_clickable(self.SOURCE_CONTAINER))
        container.click()
        time.sleep(0.5)
        input_field = self.wait.until(EC.visibility_of_element_located(self.ACTIVE_INPUT))
        input_field.send_keys(city)
        time.sleep(1.5)

    @allure.step("Enter Destination City: {city}")
    def enter_destination(self, city):
        logger.info(f"Opening Destination input view and typing: {city}")
        container = self.wait.until(EC.element_to_be_clickable(self.DESTINATION_CONTAINER))
        container.click()
        time.sleep(0.5)
        input_field = self.wait.until(EC.visibility_of_element_located(self.ACTIVE_INPUT))
        input_field.send_keys(city)
        time.sleep(1.5)

    @allure.step("Click First Suggestion")
    def click_first_suggestion(self):
        logger.info("Selecting top auto-suggest recommendation matching string query")
        suggestion_item = self.wait.until(EC.element_to_be_clickable(self.AUTO_SUGGEST_OPTIONS))
        suggestion_item.click()
        time.sleep(0.5)
        self.take_screenshot("auto_suggestion_selected")


    def _sanitize_date_input(self, travel_month, travel_day):
        # Helper to standardize raw Excel inputs into clean string match values.
        clean_day = str(int(float(travel_day)))
        clean_month = str(travel_month).strip().capitalize()
        return clean_month, clean_day

    def _is_month_visible(self, target_month_year):
        # Helper to quickly scan if a month header is active in the DOM view.
        month_header_xpath = f"//p[text()='{target_month_year}']"
        return len(self.driver.find_elements(By.XPATH, month_header_xpath)) > 0

    @allure.step("Select Dynamic Journey Date: {travel_month} {travel_day}")
    def select_journey_date(self, travel_month, travel_day):
        # to navigate the calendar and select the date.
        clean_month, clean_day = self._sanitize_date_input(travel_month, travel_day)
        target_month_year = f"{clean_month} 2026"

        logger.info(f"Initiating calendar search loop for: {target_month_year}")

        for attempt in range(3):  # Limit searching to 3 page flips max
            if self._is_month_visible(target_month_year):
                logger.info(f"Found {target_month_year} on screen! Proceeding to date selection.")
                self._click_date_element(target_month_year, clean_day)
                return True

            # If not visible, advance the calendar view forward
            logger.info(f"'{target_month_year}' hidden. Clicking Next Arrow...")
            next_arrow = self.wait.until(EC.element_to_be_clickable(self.CALENDAR_NEXT_ARROW))
            next_arrow.click()
            time.sleep(0.8)

        # Fallback closure if loop fails
        error_msg = f"CRITICAL ERR: Date '{target_month_year}' was not found within calendar limits!"
        logger.error(error_msg)
        self.take_screenshot("date_out_of_bounds_fail")
        raise Exception(error_msg)

    def _click_date_element(self, target_month_year, clean_day):
        """Helper to execute the direct JavaScript click injection on the final node."""
        dynamic_date_xpath = (
            f"//div[contains(@class, 'styles_calMnth__calCntWrp__')][descendant::p[text()='{target_month_year}']]"
            f"//p[text()='{clean_day}']"
        )
        try:
            day_element = self.wait.until(EC.presence_of_element_located((By.XPATH, dynamic_date_xpath)))
            self.driver.execute_script("arguments[0].click();", day_element)
            time.sleep(0.5)
            self.take_screenshot(f"calendar_{target_month_year.replace(' ', '_')}_{clean_day}_selected")
        except Exception as e:
            logger.error(f"Month visible but day extraction/click sequence failed: {e}")
            raise

    @allure.step("Click Search Trains Button")
    def click_search(self):
        logger.info("Triggering structural train submission processing search sequence")
        search_action_el = self.wait.until(EC.element_to_be_clickable(self.TRAIN_SEARCH_BTN))
        search_action_el.click()

    def train_data_for_csv(self, data):
        from_city = data["Source"]
        to_city = data["Destination"]
        travel_month = data["TravelMonth"]
        travel_day = data["TravelDay"]

        self.enter_source(from_city)
        self.click_first_suggestion()
        self.enter_destination(to_city)
        self.click_first_suggestion()
        self.select_journey_date(travel_month, travel_day)
        self.click_search()
        time.sleep(1)
        self.driver.execute_script("document.elementFromPoint(window.innerWidth/2, window.innerHeight/2).click();")
        time.sleep(1)

