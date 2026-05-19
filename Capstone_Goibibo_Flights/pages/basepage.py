# Contains common Selenium methods that all page classes will inherit. This avoids rewriting the same code in every page.

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, timeout = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def get_element(self, locator, condition = EC.visibility_of_element_located):
        return self.wait.until(condition(locator))

    def click(self, locator):
        self.get_element(locator, EC.visibility_of_element_located).click()

    def type(self, locator, text):
        element = self.get_element(locator, EC.visibility_of_element_located)
        element.click()
        element.send_keys(text)

    def get_text(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator)).text

    def is_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))


