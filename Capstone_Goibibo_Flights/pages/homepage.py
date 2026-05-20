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

    @allure.step("Select Hardcoded Journey Date: June 26")
    def select_hardcoded_june_date(self):
        logger.info("Targeting June 26 via direct JavaScript click invocation...")
        try:
            # Solid text-anchored XPath isolating June 2026
            june_26_xpath = (
                "//div[contains(@class, 'styles_calMnth__calCntWrp__')][descendant::p[text()='June 2026']]"
                "//p[text()='26']"
            )

            # Wait until the element exists in the DOM structure
            day_element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, june_26_xpath))
            )

            # Execute browser-level JavaScript click
            self.driver.execute_script("arguments[0].click();", day_element)
            logger.info("Successfully forced June 26 selection using execute_script!")

            time.sleep(0.5)
            self.take_screenshot("calendar_june_26_selected")

        except Exception as e:
            logger.error(f"Failed to click June 26 using JavaScript fallback: {e}")
            self.take_screenshot("hardcoded_date_fail")
            raise

    @allure.step("Click Search Trains Button")
    def click_search(self):
        logger.info("Triggering structural train submission processing search sequence")
        search_action_el = self.wait.until(EC.element_to_be_clickable(self.TRAIN_SEARCH_BTN))
        search_action_el.click()