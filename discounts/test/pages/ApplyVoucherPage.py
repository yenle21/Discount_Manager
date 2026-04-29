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
    CHECKOUT_BTN = (By.ID, "btn-checkout-now")
    VOUCHERS = (By.CSS_SELECTOR, "#promo-content > div > div:nth-child(1) > div > button")

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
        self.driver.execute_script("""
                var modal = document.getElementById('discountModal');
                if (modal) {
                    modal.classList.remove('show');
                    modal.style.display = 'none';
                }

                // 🔥 XÓA lớp backdrop (cái che màn hình)
                var backdrops = document.getElementsByClassName('modal-backdrop');
                while(backdrops.length > 0){
                    backdrops[0].parentNode.removeChild(backdrops[0]);
                }

                // reset body
                document.body.classList.remove('modal-open');
                document.body.style = '';
            """)

    def remove_voucher(self):
        self.find(*self.REMOVE_VOUCHER_BTN).click()
        wait = WebDriverWait(self.driver, 10)
        alert = wait.until(EC.alert_is_present())
        alert.accept()

    def checkout(self):
        wait = WebDriverWait(self.driver, 10, poll_frequency=0.2)
        element = self.driver.find_element(*self.CHECKOUT_BTN)

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

        import time
        time.sleep(0.5)

        element.click()

        msg = None

        for _ in range(20):  # ~2s
            try:
                alert = self.driver.switch_to.alert
                msg = alert.text
                print("ALERT:", msg)

                alert.accept()
                return msg

            except Exception:
                time.sleep(0.1)

        return None
    def enter_info(self, name="", phone="", address=""):
        self.typing(*self.NAME_INPUT, name)
        self.typing(*self.PHONE_INPUT, phone)
        self.typing(*self.ADDRESS_INPUT, address)

