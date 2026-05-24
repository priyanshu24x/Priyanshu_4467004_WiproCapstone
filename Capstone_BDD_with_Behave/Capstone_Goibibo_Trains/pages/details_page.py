# IMPORTS FOR DETAILS PAGE
from selenium.webdriver.common.by import By
from pages.basepage import BasePage
import allure
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import LogGen

logger = LogGen.loggen()


class DetailsPage(BasePage):
    # LOCATORS FOR IRCTC
    IRCTC_USERNAME_FIELD = (By.ID, "IRCTC_Username")
    IRCTC_VALIDATE_BUTTON = (By.XPATH,"//*[contains(text(), 'VALIDATE') or contains(text(), 'Validate') or contains(text(), 'SAVE')]")
    IRCTC_CHANGE_LINK = (By.XPATH, "//*[text()='Change' or contains(text(), 'Change')]")

    # LOCATORS FOR ENTERING PASSENGER DETAILS
    ADD_NEW_TRAVELLER_BUTTON = (By.XPATH, "//button[contains(., 'ADD NEW TRAVELLER')]")
    MODAL_FULL_NAME_INPUT = (By.ID, "user_name")
    MODAL_AGE_INPUT = (By.ID, "user_age")
    MODAL_GENDER_MALE = (By.XPATH, "//label[@for='Male'] | //p[text()='Male']/ancestor::label")
    MODAL_GENDER_FEMALE = (By.XPATH, "//label[@for='Female'] | //p[text()='Female']/ancestor::label")
    MODAL_SAVE_BUTTON = (By.XPATH, "//button[contains(@class, 'ModalWrap')]//p[contains(text(), 'Save')]")

    # LOCATORS FOR OTHER INPUTS AND CONTACT DETAILS
    DECLINE_FREE_CANCELLATION_RADIO = (By.XPATH, "//label[@for='getRefund_No'] | //p[contains(text(), 'No, I don')]/ancestor::label")
    CONTACT_NUMBER_INPUT = (By.ID, "contact_no")
    CONTACT_EMAIL_INPUT = (By.ID, "contact_mail_id")
    TRAVEL_INSURANCE_CHECKBOX = (By.XPATH, "//label[@for='apply_accIns']")
    PROCEED_TO_PAYMENT_BUTTON = (By.XPATH, "//button[contains(., 'Proceed to Payment')]")
    ADDED_PASSENGER_BADGE = (By.XPATH, "//p[contains(text(), '{0}')] | //span[contains(@class, 'traveller-name')]")

    # ENTERING THE IRCTC ID OF PASSENGER
    @allure.step("Force Reset and Enter IRCTC Username: {username}")
    def enter_irctc_id(self, username):

        logger.info("Checking if a pre-existing IRCTC session needs to be reset...")
        change_links = self.driver.find_elements(*self.IRCTC_CHANGE_LINK)

        if len(change_links) > 0 and change_links[0].is_displayed():
            logger.info("Pre-saved IRCTC ID detected. Clicking 'Change' link to clear state.")
            self.driver.execute_script("arguments[0].click();", change_links[0])

        logger.info(f"Interacting with credential fields -> Typing: {username}")

        username_field = self.wait.until(EC.visibility_of_element_located(self.IRCTC_USERNAME_FIELD))
        username_field.clear()
        username_field.send_keys(username)
        validate_btn = self.wait.until(EC.element_to_be_clickable(self.IRCTC_VALIDATE_BUTTON))

        self.driver.execute_script("arguments[0].click();", validate_btn)
        self.wait.until(EC.invisibility_of_element_located(self.IRCTC_VALIDATE_BUTTON))
        self.take_screenshot("irctc_id_validated")

    # FILLING THE PASSENGER DETAILS OF NAME, AGE, GENDER AND MEAL OPTION
    @allure.step("Fill Passenger Modal Details (Name: {pass_name}, Age: {pass_age}, Gender: {pass_gender}, Meal: {meal})")
    def fill_passenger_details(self, pass_name, pass_age, pass_gender, meal):

        logger.info(f"Opening Passenger Registration modal view for {pass_name}...")
        self.click(self.ADD_NEW_TRAVELLER_BUTTON)

        name_input = self.wait.until(EC.visibility_of_element_located(self.MODAL_FULL_NAME_INPUT))
        name_input.send_keys(pass_name)

        age_input = self.driver.find_element(*self.MODAL_AGE_INPUT)
        age_input.send_keys(str(pass_age))

        self.wait.until(lambda d: age_input.get_attribute("value") != "")

        if str(pass_gender).lower() == 'male':
            self.click(self.MODAL_GENDER_MALE)
        else:
            self.click(self.MODAL_GENDER_FEMALE)

        if meal:
            meal_label = str(meal).strip()
            meal_xpath = f"//span[contains(@class, 'styles_radioOuter')]//label[contains(@for, '{meal_label}') or descendant::p[text()='{meal_label}']]"
            logger.info(f"Selecting meal option: {meal_label}")

            try:
                meal_radio_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, meal_xpath)))
                meal_radio_element.click()
                logger.info(f"Meal selected: {meal_label}")

            except Exception:
                logger.info(f"Meal option not available, skipping")

        self.take_screenshot("passenger_modal_populated")
        self.click(self.MODAL_SAVE_BUTTON)

    # WAIT FOR LAYOUT TO SETTLE AND SCROLL DOWN
    @allure.step("Wait for Layout to Settle AND Scroll Viewport to Contact Information Layout Block")
    def scroll_to_element(self):

        logger.info("Applying transition pause for passenger layout settlement...")
        element = self.wait.until(EC.presence_of_element_located(self.CONTACT_NUMBER_INPUT))

        self.wait.until(EC.visibility_of_element_located(self.CONTACT_NUMBER_INPUT))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.take_screenshot("viewport_scrolling_settled")

    # SELECT THE CANCELATION ADDON
    @allure.step("Decline Free Cancellation Addon Policy")
    def select_cancellation_addon(self):

        logger.info("Selecting Cancellation Addon preferences naturally...")
        decline_insurance = self.wait.until(EC.presence_of_element_located(self.DECLINE_FREE_CANCELLATION_RADIO))

        self.driver.execute_script("arguments[0].click();", decline_insurance)

    # FILL THE CONTACT MOBILE AND EMAIL DETAILS
    @allure.step("Fill Contact Details (Mobile: {pass_mobile}, Email: {pass_email})")
    def fill_contact_information(self, pass_mobile, pass_email):

        logger.info("Filling contact details input nodes...")

        phone_el = self.wait.until(EC.visibility_of_element_located(self.CONTACT_NUMBER_INPUT))
        phone_el.clear()
        phone_el.send_keys(pass_mobile)

        email_el = self.wait.until(EC.visibility_of_element_located(self.CONTACT_EMAIL_INPUT))
        email_el.clear()
        email_el.send_keys(pass_email)

        try:
            insurance_cb = self.wait.until(EC.element_to_be_clickable(self.TRAVEL_INSURANCE_CHECKBOX))
            insurance_cb.click()

        except Exception:
            pass
        self.take_screenshot("contact_information_saved")

    # CHECK IF PASSENGER WAS ADDED
    def is_passenger_added_successfully(self, name):

        try:
            dyn_xpath = (By.XPATH, self.ADDED_PASSENGER_BADGE[1].format(name))
            element = self.wait.until(EC.visibility_of_element_located(dyn_xpath))

            return element.is_displayed()

        except Exception as e:
            logger.error(f"Passenger badge validation encountered an error: {e}")
            return False

    # PROCEED TO PAYMENT PAGE
    @allure.step("Click Proceed to Payment Button")
    def click_proceed_to_payment(self):

        logger.info("Proceeding to secure checkout payment page gateway...")

        proceed_btn = self.wait.until(EC.element_to_be_clickable(self.PROCEED_TO_PAYMENT_BUTTON))
        proceed_btn.click()

