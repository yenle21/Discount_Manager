from discounts.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/admin'


    def open_page(self):
        self.open(self.URL)

