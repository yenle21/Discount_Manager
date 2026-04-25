import time

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
        magg="test001",
        hinhthuc="Miễn phí Ship",
        loaigg="Giảm theo %",
        giatri="15",
        soluong="100",
        ngaybd="2026-05-01T10:00",
        ngaykt="2026-05-30T10:00",
        mota="Đây là voucher test tự động",
        dieukiensp="-- Tất cả sản phẩm --",
        tientoithieu="50000"
    )
    time.sleep(2)
    assert driver.current_url == 'http://127.0.0.1:5000/admin'

