# Contains locators and methods for Goibibo flight search form.

from selenium.webdriver.common.by import By
from pages.basepage import BasePage
from selenium.webdriver.support import expected_conditions as EC

class HomePage(BasePage):
    # locators
    CLOSE_POPUP = (By. XPATH, "//span[@class='sc-koXPp bDtzaf']")
    FLIGHTS_BTN = (By.XPATH,
                   "//li[contains(@class, 'header-links')]//span[text()='Flights'] | //a[contains(@href, 'flights')]")
    SOURCE_FIELD = (By.XPATH, "//input[@placeholder='From']")
    SOURCE_FROM_POPULAR_DEL = ( By.XPATH, "//span[@class='revampedCityName' and text()='New Delhi, India']")
    DESTINATION_FIELD = (By.XPATH, "//input[@placeholder='To']")
    DESTINATION_FROM_POPULAR_BOM = (By.XPATH, "//span[@class='revampedCityName' and text()='Mumbai, India']")
    FIRST_SUGGESTION = (By.XPATH, "//li[@role='option' and @data-suggestion-index='0']")
    DATE_FIELD= (By.ID, "departure")
    SEARCH_BTN = (By.XPATH, "//a[contains(@class, 'widgetSearchBtn')]")

    # methods
    def close_login_popup(self):
        try:
            self.click(self.CLOSE_POPUP)
        except:
            pass    # if popup don't appear

    def click_flights(self):
        self.wait.until(EC.visibility_of_element_located(self.FLIGHTS_BTN))
        self.click(self.FLIGHTS_BTN)

    def enter_source(self, city):
        self.type(self.SOURCE_FIELD, city)

    def select_source_suggestion(self):
        self.click(self.SOURCE_FROM_POPULAR_DEL)

    def enter_destination(self, city):
        self.type(self.DESTINATION_FIELD, city)

    def select_destination_suggestion(self):
        self.click(self.DESTINATION_FROM_POPULAR_BOM)

    def click_first_suggestion(self):
        self.wait.until(EC.visibility_of_element_located(self.FIRST_SUGGESTION))
        self.click(self.FIRST_SUGGESTION)

    def click_date_field(self):
        self.click(self.DATE_FIELD)

    def select_date(self , day, month, year):
        date_locator = (By.XPATH, f"//div[@aria-label='{month} {day} {year}']")
        self.click(date_locator)

    def click_search(self):
        self.click(self.SEARCH_BTN)

    def search_flights(self, source, destination, day, month, year):
        self.enter_source(source)
        self.click_first_suggestion()
        self.enter_destination(destination)
        self.click_first_suggestion()
        self.click_date_field()
        self.select_date(day, month, year)
        self.click_search()