# IMPORTS FOR HOMEPAGE
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.basepage import BasePage
from utils.logger import LogGen
from datetime import datetime

logger = LogGen.loggen()


class HomePage(BasePage):
    # LOCATORS FOR ENTERING INPUT DATA
    SOURCE_CONTAINER      = (By.XPATH, "//p[contains(@class, 'styles_FswFldHeading') and text()='From']")
    DESTINATION_CONTAINER = (By.XPATH, "//p[contains(@class, 'styles_FswFldHeading') and text()='To']")
    ACTIVE_INPUT          = (By.XPATH, "//input[@type='text' or @role='combobox']")
    AUTO_SUGGEST_OPTIONS  = (By.XPATH, "//div[contains(@class, 'styles_FswAutoCompItemDesc')] | //p[contains(@class, 'styles_FswAutoCompItemDescTitle')]")
    CALENDAR_NEXT_ARROW = (
        By.XPATH,
        "//button[contains(@class,'arwBtn--right')]"
    )
    VISIBLE_MONTH_HEADERS = (
        By.XPATH,
        "//div[contains(@class,'styles_calMnth__mnthNmWrp__')]//p"
    )

    TRAIN_SEARCH_BTN    = (By.XPATH, "//span[contains(@class, 'styles_FswSearchCta') and text()='SEARCH TRAINS']")
    SELECTED_SOURCE_VAL = (By.XPATH,"//p[contains(@class, 'styles_FswFldHeading') and text()='From']/following-sibling::p[1]")
    SELECTED_DESTINATION_VAL = (By.XPATH, "//p[contains(@class, 'styles_FswFldHeading') and text()='To']/following-sibling::p[1]")
    DEPARTURE_DATE_FIELD = (By.XPATH, "//p[contains(@class, 'styles_FswFldHeading') and text()='Departure Date']/..")

    # OPEN THE WEBSITE
    @allure.step("Navigate to Goibibo Trains Homepage")
    def open_goibibo(self):

        logger.info("Opening Goibibo trains page")

        self.driver.get("https://www.goibibo.com/trains/")
        self.wait.until(EC.element_to_be_clickable(self.SOURCE_CONTAINER))

        try:
            self.driver.execute_script("document.elementFromPoint(100, 100).click();")
        except:
            pass

        self.take_screenshot("goibibo_homepage_loaded")

    # CLOSE THE POPUP
    def popup_close(self):

        logger.info("closing popup")

        try:
            self.driver.execute_script("document.elementFromPoint(100, 100).click();")
        except:
            pass

    # ENTER THE FROM CITY STATION CODE AND CHOOSE FROM THE SUGGESTION LIST
    @allure.step("Enter Source City: {source_station_code}")
    def enter_source(self, source_station_code):

        logger.info("Opening Source input view and typing: {source_station_code}")

        container = self.wait.until(EC.element_to_be_clickable(self.SOURCE_CONTAINER))
        container.click()

        input_field = self.wait.until(EC.visibility_of_element_located(self.ACTIVE_INPUT))
        input_field.send_keys(source_station_code)

        self.wait.until(
            lambda driver: len(driver.find_elements(*self.AUTO_SUGGEST_OPTIONS)) > 0
            and source_station_code.lower() in driver.find_elements(*self.AUTO_SUGGEST_OPTIONS)[0].text.lower())

        suggestions = self.driver.find_elements(*self.AUTO_SUGGEST_OPTIONS)

        for option in suggestions:
            if option.is_displayed():
                option.click()
                break
        self.take_screenshot("auto_suggestion_selected")

    # ENTER THE TO CITY STATION CODE AND CHOOSE FROM THE SUGGESTION LIST
    @allure.step("Enter Destination City: {destination_station_code}")
    def enter_destination(self, destination_station_code):

        logger.info("Opening Destination input view and typing: {destination_station_code}")

        container = self.wait.until(EC.element_to_be_clickable(self.DESTINATION_CONTAINER))
        container.click()

        input_field = self.wait.until(EC.visibility_of_element_located(self.ACTIVE_INPUT))
        input_field.send_keys(destination_station_code)

        self.wait.until(
            lambda driver: len(driver.find_elements(*self.AUTO_SUGGEST_OPTIONS)) > 0
                           and destination_station_code.lower() in driver.find_elements(*self.AUTO_SUGGEST_OPTIONS)[0].text.lower())

        suggestions = self.driver.find_elements(*self.AUTO_SUGGEST_OPTIONS)
        for option in suggestions:
            if option.is_displayed():
                option.click()
                break

        self.take_screenshot("auto_suggestion_selected")

    # GET ELEMENTS THAT HAD BEEN INPUT
    def get_selected_source_text(self):

        try:
            element = self.wait.until(EC.visibility_of_element_located(self.SELECTED_SOURCE_VAL))
            return element.text

        except Exception:
            return ""

    def get_selected_destination_text(self):

        try:
            element = self.wait.until(EC.visibility_of_element_located(self.SELECTED_DESTINATION_VAL))
            return element.text

        except Exception:
            return ""

    # FINDING THE DATE WITHIN THE CALENDER
    @allure.step("Select Journey Date: {travel_month} {travel_day}")
    def select_journey_date(self, travel_month, travel_day):

        logger.info("Waiting for calendar popup")

        self.wait.until(
            EC.visibility_of_element_located(self.CALENDAR_NEXT_ARROW)
        )

        clean_month = str(travel_month).strip().capitalize()
        clean_day = str(int(float(travel_day)))

        current_year = datetime.now().year

        target_month_year = f"{clean_month} {current_year}"

        logger.info(f"Looking for: {target_month_year}")
        logger.info(f"Looking for day: {clean_day}")

        month_found = False

        for attempt in range(5):

            logger.info(f"Calendar attempt: {attempt + 1}")

            visible_months = self.driver.find_elements(
                *self.VISIBLE_MONTH_HEADERS
            )

            visible_month_texts = [
                month.text.strip()
                for month in visible_months
                if month.is_displayed()
            ]

            logger.info(f"Visible months: {visible_month_texts}")

            # TARGET MONTH FOUND
            if target_month_year in visible_month_texts:
                logger.info(f"Target month found: {target_month_year}")

                month_found = True
                break

            old_months = visible_month_texts.copy()

            logger.info("Clicking next month arrow")

            next_arrow = self.wait.until(
                EC.element_to_be_clickable(self.CALENDAR_NEXT_ARROW)
            )

            self.driver.execute_script(
                "arguments[0].click();",
                next_arrow
            )

            # WAIT FOR CALENDAR TO UPDATE
            self.wait.until(
                lambda d: [
                              m.text.strip()
                              for m in d.find_elements(*self.VISIBLE_MONTH_HEADERS)
                              if m.is_displayed()
                          ] != old_months
            )

        if not month_found:
            self.take_screenshot("month_not_found")

            raise Exception(
                f"Month '{target_month_year}' "
                f"not found after 5 attempts"
            )

        # FIND DAY INSIDE TARGET MONTH ONLY
        dynamic_day_xpath = (
            f"//div[contains(@class,'styles_calMnth__calCntWrp__')]"
            f"[.//p[text()='{target_month_year}']]"
            f"//div[contains(@class,'calDtVwWrp')]"
            f"[not(contains(@class,'grayBox'))]"
            f"//p[text()='{clean_day}']"
        )

        logger.info(f"Clicking day: {clean_day}")

        day_element = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, dynamic_day_xpath)
            )
        )

        self.driver.execute_script(
            "arguments[0].click();",
            day_element
        )

        logger.info(
            f"Date selected: {target_month_year} {clean_day}"
        )

        self.take_screenshot(
            f"date_{clean_month}_{clean_day}_selected"
        )
        
    # GOING TO THE RESULTS PAGE
    @allure.step("Click Search Trains Button")
    def click_search(self):

        logger.info("Clicking search button")

        search_action_el = self.wait.until(EC.element_to_be_clickable(self.TRAIN_SEARCH_BTN))

        search_action_el.click()
        logger.info("Search clicked")

    # SEARCH RESULTS FOR CSV DATA
    def train_data_for_csv(self, data):

        from_city    = data["Source"]
        to_city      = data["Destination"]
        travel_month = data["TravelMonth"]
        travel_day   = data["TravelDay"]

        self.enter_source(from_city)
        logger.info("Source entered")
        logger.info("Source suggestion selected")

        self.enter_destination(to_city)
        logger.info("Destination entered")
        logger.info("Destination suggestion selected")

        self.select_journey_date(travel_month, travel_day)
        logger.info("Date selected")

        self.click_search()
        logger.info("Search submitted")