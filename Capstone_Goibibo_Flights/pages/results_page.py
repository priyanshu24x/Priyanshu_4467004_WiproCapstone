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

        availability_blocks_xpath = f"//div[contains(@class, 'ticket-price-justify')]//div[contains(text(), '{class_filter}')]/parent::div/following-sibling::div//span[contains(text(), 'AVL') or contains(text(), 'AVAILABLE')]"

        blocks = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, availability_blocks_xpath)))

        for block in blocks:
            text = block.text.strip()
            numbers = re.findall(r'\d+', text)

            if numbers:
                available_count = int(numbers[0])
                logger.info(f"Checking train card: Found {available_count} seats available.")

                if available_count >= int(min_seats):
                    logger.info(f"Threshold met! Selecting train with {available_count} seats.")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", block)
                    time.sleep(0.5)
                    block.click()
                    self.take_screenshot(f"valid_train_{class_filter}_selected")
                    return True
            else:
                logger.warning(f"Could not parse digits from string: {text}")

        raise Exception(f"CRITICAL: No trains found with availability >= {min_seats} after applying filters.")