# Contains locators and methods for Goibibo flight results page.

from selenium.webdriver.common.by import By
from pages.basepage import BasePage

class ResultPage(BasePage):
    # locators
    RESULT_TITLE = (By.XPATH, "")
    FLIGHT_COMPARE_CLOSE = (By.XPATH, )

    # methods
    def close_flight_compare_popup(self):
        try:
            self.click(self.FLIGHT_COMPARE_CLOSE)
        except:
            pass # if it not appear

    def is_results_page_loaded(self):
        return self.is_visible(self.RESULT_TITLE)


