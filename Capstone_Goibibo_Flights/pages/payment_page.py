import time
import allure
from selenium.webdriver.common.by import By
from pages.basepage import BasePage
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import LogGen

logger = LogGen.loggen()


class PaymentPage(BasePage):
    # Verified working locators from your history snippet
    CREDIT_CARD_TAB = (By.XPATH, "//*[@data-testid='paymode-title' and contains(text(), 'Card')]/ancestor::li")
    CARD_NUMBER_INPUT = (By.ID, "cardNumber")
    CARD_NAME = (By.ID, "nameOnCard")
    EXPIRY_MONTH_DROPDOWN = (By.ID, "expiryMonth")
    EXPIRY_YEAR_DROPDOWN = (By.XPATH, "//input[contains(@placeholder, 'YY')] | //div[contains(text(), 'YY')]")
    CVV_INPUT = (By.ID, "cardCvv")

    PAY_NOW_BUTTON = (By.XPATH, "//button[contains(text(), 'Pay Now') or contains(text(), 'PAY')]")

    @allure.step("Fill Card Payment Details using Dynamic Excel Parameters")
    def fill_card_details(self, card_no, exp_month, exp_year, cvv, card_name):
        logger.info("Awaiting payment layout view stabilization and selecting Card Tab...")
        # 1. Click on the Credit Card tab using your working anchor strategy
        self.wait.until(EC.element_to_be_clickable(self.CREDIT_CARD_TAB)).click()
        time.sleep(0.5)  # Let the slide overlay finish rendering fields

        logger.info("Populating fields with dynamic card parameters from spreadsheet source...")

        # 2. Type Card Number
        card_field = self.wait.until(EC.visibility_of_element_located(self.CARD_NUMBER_INPUT))
        card_field.clear()
        card_field.send_keys(str(card_no))

        # 3. Dynamic Month Dropdown Intercept Click
        logger.info(f"Opening month dropdown list to pick option: {exp_month}")
        self.driver.find_element(*self.EXPIRY_MONTH_DROPDOWN).click()
        time.sleep(0.5)
        # Dynamically build the option path using your string parameter
        dynamic_month_option = (By.XPATH, f"//li[@role='option' and text()='{str(exp_month)}']")
        self.wait.until(EC.element_to_be_clickable(dynamic_month_option)).click()

        # 4. Dynamic Year Dropdown Intercept Click
        logger.info(f"Opening year dropdown list to pick option: {exp_year}")
        self.driver.find_element(*self.EXPIRY_YEAR_DROPDOWN).click()
        time.sleep(0.5)
        # Dynamically build the option path using your string parameter
        dynamic_year_option = (By.XPATH, f"//li[@role='option' and text()='{str(exp_year)}']")
        self.wait.until(EC.element_to_be_clickable(dynamic_year_option)).click()

        # 5. Type CVV Code
        cvv_field = self.driver.find_element(*self.CVV_INPUT)
        cvv_field.clear()
        cvv_field.send_keys(str(cvv))

        # 6. type in name on card
        name_card = self.wait.until(EC.visibility_of_element_located(self.CARD_NAME))
        name_card.clear()
        name_card.send_keys(str(card_name))

        self.take_screenshot("payment_form_populated")
        time.sleep(1)

    @allure.step("Click Pay Now Button")
    def click_pay_now(self):
        logger.info("Submitting payment request form...")
        self.wait.until(EC.element_to_be_clickable(self.PAY_NOW_BUTTON)).click()