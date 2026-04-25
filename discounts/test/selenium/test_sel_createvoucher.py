import time

from selenium.webdriver.common.by import By

from discounts.test.pages.LoginPage import LoginPage
from discounts.test.pages.CreateVoucherPage import CreateVoucherPage
from discounts.test.conftest import driver

def test_create_voucher_with_admin_account(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="test005",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/admin'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'thành công' in res.text

def test_create_voucher_with_customer_account(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Khách Hàng", 'khachhang', '123')
    create = CreateVoucherPage(driver=driver)
    create.open_page()
    assert driver.current_url == 'http://127.0.0.1:5000/'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'không có quyền' in res.text

# chờ dev fix để test lại
# def test_create_voucher_no_login(driver):
#     create = CreateVoucherPage(driver=driver)
#     create.open_page()
#     assert driver.current_url == 'http://127.0.0.1:5000/login'
#     res = driver.find_element(By.CLASS_NAME, 'alert')
#     assert 'đăng nhập' in res.text
# /////
def test_create_voucher_duplicate(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(1)
    create.open_page()
    create.createvoucher(
        magg="DISCOUNT10",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create = CreateVoucherPage(driver=driver)
    time.sleep(1)
    create.open_page()
    create.createvoucher(
        magg="DISCOUNT10",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'đã tồn tại' in res.text

def test_create_voucher_no_maGG(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
