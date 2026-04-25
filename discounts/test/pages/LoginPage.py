from discounts.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'
    ROLE= (By.ID, 'role')
    USERNAME = (By.ID, 'username')
    PASSWORD = (By.ID, 'pwd')
    LOGIN_BUTTON =(By.CSS_SELECTOR, '.main-container form button[type=submit]')

    def open_page(self, url=URL):
        self.open(url)

    def login(self,role, username, password):
        self.select_dropdown(*self.ROLE, role)
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.click(*self.LOGIN_BUTTON)