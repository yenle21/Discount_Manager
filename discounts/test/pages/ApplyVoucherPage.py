from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from discounts.test.pages.BasePage import BasePage


class ApplyVoucherPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart'

    CART_CONTAINER = (By.ID, "#cart1 > div > span")
    DELETE_BTN = (By.CSS_SELECTOR, "#cart1 > div > input[type='button']")
    # QUANTITY_INPUT = (By.NAME, "quantity")
    # TOTAL_PRICE = (By.ID, "total-price")

    def open_page(self):
        self.open(self.URL)

    def delete_item(self):
        self.find(*self.DELETE_BTN).click()
        self.driver.implicitly_wait(1)

        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()
    # def update_quantity(self, qty):
    #     self.typing(*self.QUANTITY_INPUT, text=str(qty))
    #
    # def get_total(self):
    #     return self.get_text(*self.TOTAL_PRICE)