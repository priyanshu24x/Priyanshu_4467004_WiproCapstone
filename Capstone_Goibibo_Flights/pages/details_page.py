from selenium.webdriver.common.by import By
from pages.basepage import BasePage
import time
import allure
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import LogGen

logger = LogGen.loggen()

class DetailsPage(BasePage):
    IRCTC_USERNAME_FIELD = (By.ID, "IRCTC_Username")    #IRCTC id and validate
    IRCTC_VALIDATE_BUTTON = (By.XPATH, "//p[contains(text(), 'VALIDATE & SAVE') or contains(text(), 'VALIDATE')]")

    ADD_NEW_TRAVELLER_BUTTON = (By.XPATH, "//p[text()='ADD NEW TRAVELLER']/ancestor::button")

    MODAL_FULL_NAME_INPUT = (By.ID, "user_name")        # Information about new traveller
    MODAL_AGE_INPUT = (By.ID, "user_age")

    MODAL_GENDER_MALE = (By.XPATH, "//label[@for='Male'] | //p[text()='Male']/ancestor::label")
    MODAL_GENDER_FEMALE = (By.XPATH, "//label[@for='Female'] | //p[text()='Female']/ancestor::label")
    MODAL_SAVE_BUTTON = (By.XPATH, "//p[text()='Save']/ancestor::button")

    DECLINE_FREE_CANCELLATION_RADIO = (By.XPATH,    # no refund insurance
                                       "//label[@for='getRefund_No'] | //p[contains(text(), 'No, I don')]/ancestor::label")
    CONTACT_NUMBER_INPUT = (By.ID, "contact_no")
    CONTACT_EMAIL_INPUT = (By.ID, "contact_mail_id")    # number and email
    TRAVEL_INSURANCE_CHECKBOX = (By.XPATH, "//label[@for='apply_accIns']")

    PROCEED_TO_PAYMENT_BUTTON = (By.XPATH, "//p[contains(text(), 'Proceed to Payment')]/ancestor::button")

    @allure.step("Enter IRCTC Username: {username}")
    def enter_irctc_id(self, username):
        username_field = self.wait.until(EC.visibility_of_element_located(self.IRCTC_USERNAME_FIELD))
        username_field.clear()
        username_field.send_keys(username)      # enters irctc id and validates it
        self.click(self.IRCTC_VALIDATE_BUTTON)
        time.sleep(1)
        self.take_screenshot("irctc_id_validated")

    @allure.step("Fill Passenger Modal Details (Name: {name}, Age: {age}, Gender: {gender})")
    def fill_passenger_details(self, name, age, gender):
        self.click(self.ADD_NEW_TRAVELLER_BUTTON)

        name_input = self.wait.until(EC.visibility_of_element_located(self.MODAL_FULL_NAME_INPUT))
        name_input.send_keys(name)  # opens new traveler and give inputs of name and age

        age_input = self.driver.find_element(*self.MODAL_AGE_INPUT)
        age_input.send_keys(str(age))
        time.sleep(0.5)

        if gender.lower() == 'male':
            self.click(self.MODAL_GENDER_MALE)  # checks male or female according to the given gender
        else:
            self.click(self.MODAL_GENDER_FEMALE)
        time.sleep(0.5)

        self.take_screenshot("passenger_modal_populated")
        self.click(self.MODAL_SAVE_BUTTON)  # save the details
        time.sleep(1.5)

    @allure.step("Wait for Passenger Modal Layout to Settle")
    def wait_for_modal_to_settle(self):     #w ait for it to close
        logger.info("Applying transition pause for passenger layout settlement...")
        # TODO: Replace with an explicit wait loop checking for ElementClickInterceptedException later
        time.sleep(1.5)

    @allure.step("Scroll Viewport to Contact Information Layout Block")
    def scroll_to_element(self):      # scrolls vertically to bottom
        element = self.wait.until(EC.presence_of_element_located(self.CONTACT_NUMBER_INPUT))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)  # Lets the scrolling animation finish completely
        self.take_screenshot("viewport_scrolling_settled")

    @allure.step("Decline Free Cancellation Addon Policy")
    def select_cancellation_addon(self):      # decline the free cancellation insurance policy
        logger.info("Selecting Cancellation Addon preferences naturally...")
        decline_insurance = self.wait.until(EC.presence_of_element_located(self.DECLINE_FREE_CANCELLATION_RADIO))
        self.driver.execute_script("arguments[0].click();", decline_insurance)

    @allure.step("Fill Contact Details (Mobile: {mobile}, Email: {email})")
    def fill_contact_information(self, mobile, email):
        logger.info("Filling contact details input nodes...")
        phone_el = self.wait.until(EC.visibility_of_element_located(self.CONTACT_NUMBER_INPUT))
        phone_el.clear()        # mobile number
        phone_el.send_keys(mobile)
        #  _el -- individual elements
        email_el = self.wait.until(EC.visibility_of_element_located(self.CONTACT_EMAIL_INPUT))
        email_el.clear()        # email
        email_el.send_keys(email)

        try:
            insurance_cb = self.wait.until(EC.element_to_be_clickable(self.TRAVEL_INSURANCE_CHECKBOX))
            insurance_cb.click()    # uncheck travel insurance. pass if already unchecked
        except Exception:
            pass
        self.take_screenshot("contact_information_saved")

    @allure.step("Click Proceed to Payment Button")
    def click_proceed_to_payment(self):
        logger.info("Proceeding to secure checkout payment page gateway...")
        proceed_btn = self.wait.until(EC.element_to_be_clickable(self.PROCEED_TO_PAYMENT_BUTTON))
        proceed_btn.click()     # payment button