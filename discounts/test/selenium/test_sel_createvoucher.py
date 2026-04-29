
import time
from datetime import datetime

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
        magg="TestVCherAdmin2",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/admin'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'thành công' in res.text
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC1.png")



def test_create_voucher_with_customer_account(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Khách Hàng", 'khachhang', '123')
    create = CreateVoucherPage(driver=driver)
    create.open_page()
    assert driver.current_url == 'http://127.0.0.1:5000/'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'không có quyền' in res.text
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC2.png")


# chờ dev fix để test lại
def test_create_voucher_no_login(driver):
    create = CreateVoucherPage(driver=driver)
    create.open_page()
    assert driver.current_url == 'http://127.0.0.1:5000/login'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'đăng nhập' in res.text
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC3.png")

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
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    create = CreateVoucherPage(driver=driver)
    time.sleep(1)
    create.open_page()
    create.createvoucher(
        magg="DISCOUNT10",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'đã tồn tại' in res.text
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC4.png")


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
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC5.png")

def test_voucher_special_characters(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="SALE@#123",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')

    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC6.png")

def test_create_voucher_with_code_too_long(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TESTDODAICUAMAGIAMGIA",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/admin'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC7.png")

def test_create_voucher_with_start_day_in_past(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC08",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="04262026", ngaybd_time="0135P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC8.png")

def test_create_voucher_with_end_day_gt_start_day(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")

    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC08",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1000A",
        ngaykt_date="05012026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC9.png")

def test_create_voucher_start_day_eq_current(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    now = datetime.now()
    current_date = now.strftime("%m%d%Y")  # Trả ra kiểu: "04262026"

    gio_phut = now.strftime("%I%M")
    am_pm = "A" if now.hour < 12 else "P"
    current_time = gio_phut + am_pm
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC10",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date=current_date, ngaybd_time=current_time,
        ngaykt_date="05012026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()

    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/admin'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC10.png")

def test_create_voucher_end_day_eq_start_day(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC08",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1159P",
        ngaykt_date="05012026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC11.png")


def test_create_voucher_no_input_start_day(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC08",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="", ngaybd_time="",
        ngaykt_date="05012026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC12.png")

def test_create_voucher_no_input_end_day(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC08",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1159P",
        ngaykt_date="", ngaykt_time="",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    time.sleep(1)
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC13.png")

def test_create_voucher_gt_50percent(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC21",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="51",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    input_element = driver.find_element(By.NAME, "GiaTri")
    actual_value = input_element.get_attribute("value")
    assert int(actual_value) <= 50

    create.click_save()
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC14.png")

def test_create_voucher_amount_exceeds_limit(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TCMAU",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="1000000000",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC15.png")

def test_create_voucher_with_0_percent(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC0percent",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="0",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC16a.png")
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_0_price(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC0percent",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="0",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )

    create.click_save()
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC17.png")
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_chu(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC0percent",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="abc",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )

    create.click_save()
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC18.png")
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')


def test_create_voucher_with_negative_percent(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC0percent",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="-100",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )

    create.click_save()
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC19.png")
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')



def test_create_voucher_with_negative_price(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TC0percent",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="-10000",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )

    create.click_save()
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC20.png")
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_cate(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TestHehe",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="100",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/admin'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC21.png")
    e = driver.find_element(By.CSS_SELECTOR, "table > tbody > tr:first-child > td:nth-child(9)")
    assert "Sữa" in e.text
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_number_float(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TestHehe",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="1.5",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC23.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_no_DieuKien(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TestDieuKienToiThieu",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="1",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu=""
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/admin'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC22.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_number_0(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TetSoluong0",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="0",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC24.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_negative_number(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TetSoluong0",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="-1000",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC25.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_number_is_chu(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TetSoluong0",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="abcd",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC26.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_code_space(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="SALE 10",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="1",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC27.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')

def test_create_voucher_with_code_chu_hoa_chu_thuong(driver):
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
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    create = CreateVoucherPage(driver=driver)
    time.sleep(1)
    create.open_page()
    create.createvoucher(
        magg="discount10",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd_date="05012026", ngaybd_time="1000A",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    res = driver.find_element(By.CLASS_NAME, 'alert')
    assert 'đã tồn tại' in res.text
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC28.png")

def test_create_voucher_with_long_number(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    create = CreateVoucherPage(driver=driver)
    time.sleep(2)
    create.open_page()
    create.createvoucher(
        magg="TetSoluong0",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo số tiền",
        giatri="10000",
        soluong="999999999",
        ngaybd_date="05102026", ngaybd_time="1159P",
        ngaykt_date="05302026", ngaykt_time="1159P",
        mota="Đây là voucher test tự động",
        dieukiensp="Sữa",
        tientoithieu="50000"
    )

    create.click_save()
    assert driver.current_url == 'http://127.0.0.1:5000/create'
    driver.save_screenshot("discounts/test/screenshots/CreateVoucher/actual_output_TC29.png")
    # res = driver.find_element(By.CLASS_NAME, 'alert')
