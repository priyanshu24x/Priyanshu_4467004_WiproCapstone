# IMPORTS FOR BASEPAGE
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    # FINDS THE LOCATOR
    def get_element(self, locator, condition=EC.visibility_of_element_located):
        return self.wait.until(condition(locator))

    # CLICKS ON THE LOCATOR
    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    # TYPES THE LOCATOR
    def type(self, locator, text):
        element = self.get_element(locator, EC.visibility_of_element_located)
        element.clear()
        element.send_keys(text)

    # FINDS THE LOCATOR
    def get_text(self, locator):
        return self.get_element(locator, EC.presence_of_element_located).text

    # CHECK IF LOCATOR IS PRESENT
    def is_visible(self, locator):
        try:
            return self.get_element(locator, EC.visibility_of_element_located).is_displayed()
        except:
            return False

    # TAKES A SCREENSHOT
    def take_screenshot(self, name: str):
        screenshot_path = f"reports/screenshots/{name}.png"
        self.driver.save_screenshot(screenshot_path)

        with open(screenshot_path, "rb") as image_file:
            allure.attach(
                image_file.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )