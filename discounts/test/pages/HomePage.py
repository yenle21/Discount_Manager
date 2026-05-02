from discounts.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class HomePage(BasePage):
    URL = 'http://127.0.0.1:5000/'

    SEARCH_INPUT = (By.CSS_SELECTOR, '.search-section > div > form > input')
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".search-section > div > form > button[type='submit']")
    PRODUCT_BUTTON1 = (By.CSS_SELECTOR, '.product-grid > div:nth-child(1) > div > button')
    PRODUCT_BUTTON2 = (By.CSS_SELECTOR, '.product-grid > div:nth-child(2) > div > button')

    PRODUCT_BUTTON3 = (By.CSS_SELECTOR, '.product-grid > div:nth-child(2) > div.p-3 > button')
    LOGO = (By.CSS_SELECTOR, 'body > nav > div > a')
    LOGIN_BUTTON = (By.CSS_SELECTOR, '#mynavbar > li:nth-child(2) > a')
    REGISTER_BUTTON = (By.CSS_SELECTOR, '#mynavbar > li:nth-child(3) > a')
    LOGOUT_BUTTON = (By.CSS_SELECTOR, '#mynavbar > li:nth-child(3) > a')
    VOUCHER_MANAGER = (By.ID, "voucher-manager")
    CART_MANAGER = (By.CSS_SELECTOR, ".sidebar > nav > a:nth-child(2)")
    USER_NAME = (By.CSS_SELECTOR, '#mynavbar > li:nth-child(2) > a')

    CATEGORY_DROPDOWN = (By.CSS_SELECTOR, ".search-section > div > form > button[type='button']")
    CATEGORY_ITEMS = (By.CSS_SELECTOR, ".search-section > div > form > ul > li > a")
    PRODUCT_NAMES = (By.CLASS_NAME, "product-title")
    CART_COUNTER = (By.ID, "cart-counter")

    BACK_HOME_BTN = (By.CSS_SELECTOR, ".product-grid > div > a")
    PAGE_LINKS = (By.CSS_SELECTOR, ".pagination .page-link")
    ACTIVE_PAGE = (By.CSS_SELECTOR, ".pagination .page-item.active .page-link")

    def open_page(self):
        self.open(self.URL)

    def search(self, kw):
        self.typing(*self.SEARCH_INPUT, kw)
        self.click(*self.SEARCH_BUTTON)

    def add_to_cart(self):
        self.click(*self.PRODUCT_BUTTON1)
        self.driver.implicitly_wait(1)
        self.click(*self.PRODUCT_BUTTON1)
        self.driver.implicitly_wait(1)
        self.click(*self.PRODUCT_BUTTON2)

    def add_to_cart_not_milk(self):
        self.click(*self.PRODUCT_BUTTON3)
        self.driver.implicitly_wait(1)

    def click_logo(self):
        self.click(*self.LOGO)

    def click_login(self):
        self.click(*self.LOGIN_BUTTON)

    def click_register(self):
        self.click(*self.REGISTER_BUTTON)

    def click_logout(self):
        self.click(*self.LOGOUT_BUTTON)

    def click_cart(self):
        self.click(*self.CART_MANAGER)

    def get_username(self):
        return self.wait.until(lambda d: d.find_element(*self.USER_NAME)).text

    def is_login_visible(self):
        elements = self.finds(*self.LOGIN_BUTTON)
        return any(e.is_displayed() and "Đăng nhập" in e.text for e in elements)

    def is_register_visible(self):
        elements = self.finds(*self.REGISTER_BUTTON)
        return any(e.is_displayed() and "Đăng ký" in e.text for e in elements)

    def is_logout_visible(self):
        elements = self.finds(*self.LOGOUT_BUTTON)
        return any(e.is_displayed() and "Đăng xuất" in e.text for e in elements)

    def is_voucher_visible(self):
        elements = self.finds(*self.VOUCHER_MANAGER)
        return any(e.is_displayed() for e in elements)

    def open_category_dropdown(self):
        self.click(*self.CATEGORY_DROPDOWN)

    def get_all_categories(self):
        return self.finds(*self.CATEGORY_ITEMS)

    def select_category(self, name):
        items = self.finds(*self.CATEGORY_ITEMS)
        for item in items:
            if name in item.text:
                item.click()
                return

    def get_product_names(self):
        elements = self.finds(*self.PRODUCT_NAMES)
        return [e.text for e in elements if e.is_displayed()]

    def click_back_home(self):
        self.click(*self.BACK_HOME_BTN)

    def safe_click(self, element):

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)

    def click_page(self, number):
        pages = self.driver.find_elements(*self.PAGE_LINKS)

        for p in pages:
            if p.text.strip() == str(number):
                self.safe_click(p)
                return

        raise Exception(f"Không tìm thấy page {number}")

    def get_active_page(self):
        return self.wait.until(
            lambda d: d.find_element(*self.ACTIVE_PAGE)
        ).text.strip()

    def get_cart_count(self):
        return int(
            self.wait.until(
                lambda d: d.find_element(*self.CART_COUNTER).text
            )
        )

    def logout_if_needed(self):
        if self.is_logout_visible():
            self.click_logout()