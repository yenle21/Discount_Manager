import time

import pyautogui
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
    PAYMENT_METHODS = (By.ID, "payment-method")
    DISCOUNT_AMOUNT = (By.ID, "discount-val")

    NAME_INPUT = (By.ID, "receiver-name")
    PHONE_INPUT = (By.ID, "receiver-phone")
    ADDRESS_INPUT = (By.ID, "receiver-address")

    TABS = (By.CSS_SELECTOR, "#aplied-vouchers-success .badge")
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

    def get_all_alerts(self, timeout=3):
        wait = WebDriverWait(self.driver, timeout, poll_frequency=0.2)

        messages = []

        for _ in range(2):  # tối đa 2 alert (confirm + result)
            try:
                alert = wait.until(EC.alert_is_present())
                msg = alert.text
                print("ALERT:", msg)
                alert.accept()

                messages.append(msg)
            except:
                break

        return messages

    def checkout(self):
        element = self.driver.find_element(*self.CHECKOUT_BTN)

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

        import time
        time.sleep(0.5)

        element.click()

    def enter_info(self, name="", phone="", address=""):
        self.typing(*self.NAME_INPUT, name)
        self.typing(*self.PHONE_INPUT, phone)
        self.typing(*self.ADDRESS_INPUT, address)

    def get_payment(self):
        element = self.find(*self.PAYMENT_METHODS)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        import time
        time.sleep(0.5)
        element.click()

    def select_voucher_tab(self, tab_name):
        if "khuyến" in tab_name.lower():
            self.driver.find_element(By.ID, "promo-tab").click()
        elif "ship" in tab_name.lower():
            self.driver.find_element(By.ID, "ship-tab").click()
        else:
            raise Exception(f"Không tìm thấy tab: {tab_name}")

    def get_discount_amount(self):
        return self.find(*self.DISCOUNT_AMOUNT).text

    def select_voucher_by_code(self, code):
        items = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#promo-content .card, #promo-content .voucher"
        )

        for item in items:
            if code.lower() in item.text.lower():
                item.click()
                return

        raise Exception(f"Không tìm thấy voucher: {code}")

    def get_applied_vouchers(self):
        items = self.driver.find_elements(
            By.CSS_SELECTOR,
            "#applied-vouchers-success .badge"
        )

        return [i.text.strip() for i in items]

    def get_voucher_texts(self, content_id):
        items = self.driver.find_elements(
            By.CSS_SELECTOR,
            f"#{content_id} .card, "
            f"#{content_id} .voucher, "
            f"#{content_id} .list-group-item"
        )

        texts = [i.text.strip() for i in items if i.text.strip()]

        return texts


