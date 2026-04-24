from discounts.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CartPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart'

    PROD1_QUANTITY = (By.CSS_SELECTOR, 'tbody tr:nth-child(1) td:nth-child(4) > input')
    PROD2_QUANTITY = (By.CSS_SELECTOR, 'tbody tr:nth-child(2) td:nth-child(4) > input')
    PAY_BUTTON = (By.CSS_SELECTOR, '.container button')

    def open_page(self):
        self.open(self.URL)

    def add_receipt(self):
        # self.driver.implicitly_wait(1)
        # self.typing(*self.PROD1_QUANTITY, 5)
        # self.driver.implicitly_wait(1)
        # self.typing(*self.PROD2_QUANTITY, 2)
        # self.driver.implicitly_wait(1)
        self.click(*self.PAY_BUTTON)

        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()