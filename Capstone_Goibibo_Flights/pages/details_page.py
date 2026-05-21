from selenium.webdriver.common.by import By
from pages.basepage import BasePage
import time
import allure
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import LogGen

logger = LogGen.loggen()


class DetailsPage(BasePage):
    # Using '//*' ensures Selenium finds it regardless of whether it's a div, p, span, or button container
    IRCTC_USERNAME_FIELD = (By.ID, "IRCTC_Username")
    IRCTC_VALIDATE_BUTTON = (By.XPATH,
                             "//*[contains(text(), 'VALIDATE') or contains(text(), 'Validate') or contains(text(), 'SAVE')]")
    IRCTC_CHANGE_LINK = (By.XPATH, "//*[text()='Change' or contains(text(), 'Change')]")

    # Fixed: Targets the actual blue outline action button container visible in your screenshot
    ADD_NEW_TRAVELLER_BUTTON = (By.XPATH, "//button[contains(., 'ADD NEW TRAVELLER')]")

    MODAL_FULL_NAME_INPUT = (By.ID, "user_name")
    MODAL_AGE_INPUT = (By.ID, "user_age")

    MODAL_GENDER_MALE = (By.XPATH, "//label[@for='Male'] | //p[text()='Male']/ancestor::label")
    MODAL_GENDER_FEMALE = (By.XPATH, "//label[@for='Female'] | //p[text()='Female']/ancestor::label")
    # This looks for a paragraph tag containing the text 'Save', ignoring any hidden spaces, inside a button
    MODAL_SAVE_BUTTON = (By.XPATH, "//button[contains(@class, 'ModalWrap')]//p[contains(text(), 'Save')]")
    DECLINE_FREE_CANCELLATION_RADIO = (By.XPATH,
                                       "//label[@for='getRefund_No'] | //p[contains(text(), 'No, I don')]/ancestor::label")
    CONTACT_NUMBER_INPUT = (By.ID, "contact_no")
    CONTACT_EMAIL_INPUT = (By.ID, "contact_mail_id")
    TRAVEL_INSURANCE_CHECKBOX = (By.XPATH, "//label[@for='apply_accIns']")

    # Fixed: Targets the main orange wrapper button visible on the right sidebar
    PROCEED_TO_PAYMENT_BUTTON = (By.XPATH, "//button[contains(., 'Proceed to Payment')]")

    @allure.step("Force Reset and Enter IRCTC Username: {username}")
    def enter_irctc_id(self, username):
        logger.info("Checking if a pre-existing IRCTC session needs to be reset...")

        # 1. Look for 'Change' anchor link
        change_links = self.driver.find_elements(*self.IRCTC_CHANGE_LINK)
        if len(change_links) > 0 and change_links[0].is_displayed():
            logger.info("Pre-saved IRCTC ID detected. Clicking 'Change' link to clear state.")
            self.driver.execute_script("arguments[0].click();", change_links[0])
            time.sleep(0.5)

        # 2. Enter new profile credentials cleanly
        logger.info(f"Interacting with credential fields -> Typing: {username}")
        username_field = self.wait.until(EC.visibility_of_element_located(self.IRCTC_USERNAME_FIELD))
        username_field.clear()
        username_field.send_keys(username)

        # 3. Commit profile authentication click
        validate_btn = self.wait.until(EC.element_to_be_clickable(self.IRCTC_VALIDATE_BUTTON))
        self.driver.execute_script("arguments[0].click();", validate_btn)

        time.sleep(1)
        self.take_screenshot("irctc_id_validated")

    # FIXED INDENTATION: This method is now a proper first-class sibling method of the class!
    @allure.step("Fill Passenger Modal Details (Name: {name}, Age: {age}, Gender: {gender}, Meal: {meal})")
    def fill_passenger_details(self, name, age, gender, meal):
        logger.info(f"Opening Passenger Registration modal view for {name}...")
        self.click(self.ADD_NEW_TRAVELLER_BUTTON)

        name_input = self.wait.until(EC.visibility_of_element_located(self.MODAL_FULL_NAME_INPUT))
        name_input.send_keys(name)

        age_input = self.driver.find_element(*self.MODAL_AGE_INPUT)
        age_input.send_keys(str(age))
        time.sleep(0.5)

        if str(gender).lower() == 'male':
            self.click(self.MODAL_GENDER_MALE)
        else:
            self.click(self.MODAL_GENDER_FEMALE)
        time.sleep(0.5)

        # Dynamic Meal Option Selection Block
        if meal:
            meal_label = str(meal).strip()
            meal_xpath = f"//span[contains(@class, 'styles_radioOuter')]//label[contains(@for, '{meal_label}') or descendant::p[text()='{meal_label}']]"
            logger.info(f"Selecting dynamic meal option radio button: {meal_label}")
            try:
                meal_radio_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, meal_xpath)))
                meal_radio_element.click()
            except Exception:
                logger.info("Standard meal click intercepted. Falling back to JavaScript injection...")
                meal_node = self.driver.find_element(By.XPATH, meal_xpath)
                self.driver.execute_script("arguments[0].click();", meal_node)
        time.sleep(0.5)

        self.take_screenshot("passenger_modal_populated")
        self.click(self.MODAL_SAVE_BUTTON)
        time.sleep(1.5)

    @allure.step("Wait for Passenger Modal Layout to Settle")
    def wait_for_modal_to_settle(self):
        logger.info("Applying transition pause for passenger layout settlement...")
        time.sleep(1)

    @allure.step("Scroll Viewport to Contact Information Layout Block")
    def scroll_to_element(self):
        element = self.wait.until(EC.presence_of_element_located(self.CONTACT_NUMBER_INPUT))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.take_screenshot("viewport_scrolling_settled")

    @allure.step("Decline Free Cancellation Addon Policy")
    def select_cancellation_addon(self):
        logger.info("Selecting Cancellation Addon preferences naturally...")
        decline_insurance = self.wait.until(EC.presence_of_element_located(self.DECLINE_FREE_CANCELLATION_RADIO))
        self.driver.execute_script("arguments[0].click();", decline_insurance)

    @allure.step("Fill Contact Details (Mobile: {mobile}, Email: {email})")
    def fill_contact_information(self, mobile, email):
        logger.info("Filling contact details input nodes...")
        phone_el = self.wait.until(EC.visibility_of_element_located(self.CONTACT_NUMBER_INPUT))
        phone_el.clear()
        phone_el.send_keys(mobile)

        email_el = self.wait.until(EC.visibility_of_element_located(self.CONTACT_EMAIL_INPUT))
        email_el.clear()
        email_el.send_keys(email)

        try:
            insurance_cb = self.wait.until(EC.element_to_be_clickable(self.TRAVEL_INSURANCE_CHECKBOX))
            insurance_cb.click()
        except Exception:
            pass
        self.take_screenshot("contact_information_saved")

    @allure.step("Click Proceed to Payment Button")
    def click_proceed_to_payment(self):
        logger.info("Proceeding to secure checkout payment page gateway...")
        proceed_btn = self.wait.until(EC.element_to_be_clickable(self.PROCEED_TO_PAYMENT_BUTTON))
        proceed_btn.click()