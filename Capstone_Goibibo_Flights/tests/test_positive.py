import pytest
import time

from pages.homepage import HomePage


def test_home(driver):
    home_page = HomePage(driver)
    time.sleep(23)