from selenium.webdriver.common.by import By

from discounts.test.pages.BasePage import BasePage


class RegisterPage(BasePage):
    URL = 'http://127.0.0.1:5000/register'
    NAME = (By.ID, 'name')
    USERNAME = (By.ID, 'username')
    PASSWORD = (By.ID, 'password')
    CONFIRM = (By.ID, 'confirm')
    EMAIL = (By.ID, 'email')
    BUTTON_REGISTER = (By.CSS_SELECTOR, 'form button[type=submit]')

    def open_page(self):
        self.open(self.URL)

    def upload_avatar(self, file_path):
        file_input = self.driver.find_element(By.ID, "avatar")
        file_input.send_keys(file_path)

    def register(self,name,username,password,confirm,email, avatar_path=None):
        self.typing(*self.NAME,name)
        self.typing(*self.USERNAME,username)
        self.typing(*self.PASSWORD,password)
        self.typing(*self.CONFIRM,confirm)
        self.typing(*self.EMAIL,email)
        if avatar_path: #upload ảnh nếu có file_path
            self.upload_avatar(avatar_path)
        self.driver.implicitly_wait(1)
        self.click(*self.BUTTON_REGISTER)
