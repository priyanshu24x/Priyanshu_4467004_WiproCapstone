import time
import allure
from selenium.webdriver.common.by import By
from pages.basepage import BasePage
from selenium.webdriver.support import expected_conditions as EC


class PaymentPage(BasePage):
    CREDIT_CARD_TAB = (By.XPATH, "//*[@data-testid='paymode-title' and contains(text(), 'Card')]/ancestor::li")

    CARD_NUMBER_INPUT = (By.ID, "cardNumber")
    EXPIRY_MONTH_DROPDOWN = (By.ID, "expiryMonth")  # card information
    EXPIRY_YEAR_DROPDOWN = (By.XPATH, "//input[contains(@placeholder, 'YY')] | //div[contains(text(), 'YY')]")
    CVV_INPUT = (By.ID, "cardCvv")

    SELECT_MARCH = (By.XPATH, "//li[@role='option' and text()='03']")   # expiration date
    SELECT_2028 = (By.XPATH, "//li[@role='option' and text()='2028']")

    @allure.step("Navigate to Credit/Debit Card Form Mode")
    def navigate_to_credit_card_form(self):     # payment mode -- credit card
        self.wait.until(EC.element_to_be_clickable(self.CREDIT_CARD_TAB)).click()
        self.take_screenshot("credit_card_tab_selected")

    @allure.step("Fill Mock Financial Card Details (Card No: {card_no}, CVV: ***)")
    def fill_mock_card_details(self, card_no, cvv):
        card_field = self.wait.until(EC.visibility_of_element_located(self.CARD_NUMBER_INPUT))
        card_field.send_keys(card_no)   #3 card number

        self.driver.find_element(*self.EXPIRY_MONTH_DROPDOWN).click()
        time.sleep(0.5)     # clicks and give the month drop down, click the required month
        self.wait.until(EC.element_to_be_clickable(self.SELECT_MARCH)).click()

        self.driver.find_element(*self.EXPIRY_YEAR_DROPDOWN).click()
        time.sleep(0.5)     # # clicks and give the year drop down, click the required year
        self.wait.until(EC.element_to_be_clickable(self.SELECT_2028)).click()

        self.driver.find_element(*self.CVV_INPUT).send_keys(cvv)
        self.take_screenshot("payment_form_populated")