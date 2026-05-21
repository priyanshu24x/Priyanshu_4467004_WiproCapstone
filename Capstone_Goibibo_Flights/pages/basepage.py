# Contains common Selenium methods that all page classes will inherit.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.screenshot import ScreenshotUtil
import allure
from selenium.webdriver.remote.webdriver import WebDriver

class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def get_element(self, locator, condition=EC.visibility_of_element_located):
        return self.wait.until(condition(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()


    def type(self, locator, text):
        element = self.get_element(locator, EC.visibility_of_element_located)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self.get_element(locator, EC.presence_of_element_located).text


    def is_visible(self, locator):
        try:
            return self.get_element(locator, EC.visibility_of_element_located).is_displayed()
        except:
            return False

    def take_screenshot(self, name: str):
        screenshot_path = f"reports/screenshots/{name}.png"
        # 1. Save the file locally to your system directory as usual
        self.driver.save_screenshot(screenshot_path)

        # 2. Attach it directly to the active Allure test context
        with open(screenshot_path, "rb") as image_file:
            allure.attach(
                image_file.read(),
                name=name,
                attachment_type=allure.attachment_type.PNG
            )