from discounts.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class AdminPage(BasePage):
    URL = 'http://127.0.0.1:5000/admin'


    def open_page(self):
        self.open(self.URL)

