from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from discounts.test.pages.BasePage import BasePage


class ApplyVoucherPage(BasePage):
    URL = 'http://127.0.0.1:5000/cart'

    CART_CONTAINER = (By.ID, "#cart1 > div > span")
    DELETE_BTN = (By.CSS_SELECTOR, "#cart1 > div > input[type='button']")
    QUANTITY_INPUT = (By.CSS_SELECTOR, "#cart1 > div > input[type='number']")
    TOTAL_PRICE = (By.CLASS_NAME, "cart-price")
    PRICE_AFTER_VOUCHER = (By.CLASS_NAME, "cart-new-price")

    VOUCHER_BTN = (By.ID, "apply-voucher-btn")
    REMOVE_VOUCHER_BTN = (By.ID, "btn-clear-vouchers")
    CHECKOUT_BTN = (By.XPATH, "btn-checkout-now")
    VOUCHERS = (By.CSS_SELECTOR, "#promo-content > div > div:nth-child(1) > div")

    NAME_INPUT = (By.ID, "receiver-name")
    PHONE_INPUT = (By.ID, "receiver-phone")
    ADDRESS_INPUT = (By.ID, "receiver-address")

    def open_page(self):
        self.open(self.URL)

    def delete_item(self):
        self.find(*self.DELETE_BTN).click()
        self.driver.implicitly_wait(1)

        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()

    def update_quantity(self, qty):
        e = self.find(*self.QUANTITY_INPUT)
        e.clear()
        e.send_keys(str(qty))
        self.driver.implicitly_wait(1)

    def get_quantity(self):
        return self.find(*self.QUANTITY_INPUT).get_attribute("value")

    def get_total(self):
        return self.find(*self.TOTAL_PRICE).text

    def get_total_new(self):
        return self.find(*self.PRICE_AFTER_VOUCHER).text

    def open_voucher(self):
        self.driver.find_element(*self.VOUCHER_BTN).click()

    def choose_voucher(self):
        self.driver.find_element(*self.VOUCHERS).click()
        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()

    def remove_voucher(self):
        self.driver.find_element(*self.REMOVE_VOUCHER_BTN).click()
        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()

    def checkout(self):
        self.driver.find_element(*self.CHECKOUT_BTN).click()

    def enter_info(self, name="", phone="", address=""):
        self.driver.find_element(*self.NAME_INPUT).send_keys(name)
        self.driver.find_element(*self.PHONE_INPUT).send_keys(phone)
        self.driver.find_element(*self.ADDRESS_INPUT).send_keys(address)

