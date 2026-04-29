from selenium.webdriver.common.by import By

from discounts.test.pages.AdminPage import AdminPage
from discounts.test.pages.HomePage import HomePage
from discounts.test.pages.LoginPage import LoginPage
from discounts.test.conftest import driver

def test_login_success_with_admin_account(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Quản Trị Viên", "admin", "123")
    assert driver.current_url == "http://127.0.0.1:5000/admin"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC1.png")

def test_login_success_with_customer_account(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Khách Hàng", "khachhang", "123")
    res = driver.find_element(By.CSS_SELECTOR, '#mynavbar > li:nth-child(2) > a')
    assert 'Khách' in res.text
    assert driver.current_url == "http://127.0.0.1:5000/"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC2.png")

def test_login_fail_with_wrong_username(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Khách Hàng", "admin", "123")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC3.png")

def test_login_fail_with_wrong_password(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Khách Hàng", "khachhang", "456")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC4.png")

def test_login_fail_with_wrong_role(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Quản Trị Viên", "khachhang", "123")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC5.png")

def test_login_fail_with_no_input_username(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Quản Trị Viên", "", "123")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC6.png")

def test_login_fail_with_no_input_password(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Quản Trị Viên", "admin", "")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC7.png")

def test_login_fail_with_no_input_password_username(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Quản Trị Viên", "", "")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC8.png")

def test_login_fail_with_username_special_charaters(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Quản Trị Viên", "admin@123", "123")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC9.png")

def test_redict_page_admin_no_login(driver):
   admin = AdminPage(driver=driver)
   admin.open_page()
   assert driver.current_url == "http://127.0.0.1:5000/login"
   driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC10.png")

def test_redict_page_customer_no_login(driver):
    home = HomePage(driver=driver)
    home.open_page()
    res = driver.find_element(By.CSS_SELECTOR, '#mynavbar > li:nth-child(2) > a')
    assert 'Khách' not in res.text
    assert driver.current_url == "http://127.0.0.1:5000/"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC11.png")

def test_login_with_username_space(driver):
    login_page = LoginPage(driver=driver)
    login_page.open_page()
    login_page.login("Khách Hàng", "khach hang", "123")
    assert driver.current_url == "http://127.0.0.1:5000/login"
    driver.save_screenshot("discounts/test/screenshots/Login/actual_output_TC12.png")
