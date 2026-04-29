import time

from selenium.webdriver.common.by import By

from discounts.test.pages.LoginPage import LoginPage
from discounts.test.pages.RegisterPage import RegisterPage


def test_register_success(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Nguyễn Văn A",
        username="newuser",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    time.sleep(3)
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Khách Hàng", 'newuser', 'Khachhang@123')

    res = driver.find_element(By.CSS_SELECTOR, '#mynavbar > li:nth-child(2) > a')
    assert 'A' in res.text
    assert driver.current_url == 'http://127.0.0.1:5000/'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC1.png")

def test_register_failure_with_empty_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Nguyễn Văn A",
        username="",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC2.png")



def test_register_failure_with_empty_password(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Nguyễn Văn A",
        username="newuser123",
        password="",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC3.png")


def test_register_failure_with_empty_confirm_password(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Nguyễn Văn A",
        username="newuser123",
        password="Khachhang@123",
        confirm="",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC4.png")


def test_register_failure_with_empty_email(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Nguyễn Văn A",
        username="newuser123",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC5.png")


def test_register_failure_with_empty_name(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="",
        username="newuser123",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC6.png")


def test_register_failure_with_empty_all(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="",
        username="",
        password="",
        confirm="",
        email="",
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC7.png")



def test_register_failure_with_duplicate_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="khachhang ",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC8.png")


def test_register_failure_with_special_characters_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="khach@#123 ",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC9.png")

    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC9.png")

def test_register_failure_with_space_username(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="khach hang ",
        password="Khachhang@123",
        confirm="Khachhang@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC10.png")


def test_register_failure_with_password_mismatch(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="newusertest",
        password="Khachhang@123",
        confirm="Khachhang@456",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC11.png")


def test_register_failure_with_password_valid(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="newuser123",
        password="Admin@123",
        confirm="Admin@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/login'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC12.png")

def test_register_failure_with_password_7_characters(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="Admin@1",
        confirm="Admin@1",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC13.png")

def test_register_failure_with_password_no_uppercase(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="admin@123" ,
        confirm="admin@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC14.png")


def test_register_failure_with_password_no_special_characters(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="Admin1234" ,
        confirm="Admin1234  ",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC15.png")


def test_register_failure_with_password_no_number(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="Admin@abc" ,
        confirm="Admin@abc",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC16.png")


def test_register_failure_with_password_lowercase(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="abcdefgh@123" ,
        confirm="abcdefgh@123",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC17.png")

def test_register_failure_with_password_only_numbers(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="12345678" ,
        confirm="12345678",
        email="test@gmail.com",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC18.png")

def test_register_failure_with_email_invalid(driver):
    register = RegisterPage(driver=driver)
    register.open_page()

    register.register(
        name="Lê Minh Khôi",
        username="admin123",
        password="Admin@123" ,
        confirm="Admin@123",
        email="abcgmail ",
        avatar_path="D:/HK2_2025/KiemThu/Discount_Manager/discounts/static/images/test_avatar.png"  # optional
    )
    assert driver.current_url == 'http://127.0.0.1:5000/register'
    driver.save_screenshot("discounts/test/screenshots/Register/actual_output_TC19.png")

