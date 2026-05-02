"""
=============================================================================
FILE: test_sel_search_and_checkout.py
MODULE 2: Thanh toán (/cart)
=============================================================================

KỊCH BẢN TEST – TÌM KIẾM VOUCHER
─────────────────────────────────────────────────────────────────────────────
TC_SEARCH_01  Tìm đúng mã → hiển thị đúng 1 kết quả khớp
TC_SEARCH_02  Tìm chuỗi con → hiển thị tất cả kết quả khớp
TC_SEARCH_03  Tìm không tồn tại → bảng trống / không có kết quả
TC_SEARCH_04  Tìm ô trống → hiển thị toàn bộ danh sách
TC_SEARCH_05  Tìm không phân biệt hoa/thường
TC_SEARCH_06  Lọc Trạng thái "active" → chỉ badge active
TC_SEARCH_07  Lọc Trạng thái "pending" → chỉ badge pending
TC_SEARCH_08  Lọc Trạng thái "expired" → chỉ badge expired
TC_SEARCH_09  Lọc Hình thức "Khuyến mãi" → chỉ badge đỏ
TC_SEARCH_10  Lọc Hình thức "Shipping" → chỉ badge xanh
TC_SEARCH_11  Kết hợp keyword + trạng thái → kết quả giao nhau
TC_SEARCH_12  Đặt lại "Tất cả" → hiển thị lại đầy đủ

KỊCH BẢN TEST – THANH TOÁN
─────────────────────────────────────────────────────────────────────────────
TC_CK_01  Thanh toán COD không voucher → thành công
TC_CK_02  Thanh toán Chuyển khoản + voucher → tổng giảm, thành công
TC_CK_03  Bỏ trống Tên người nhận → cảnh báo
TC_CK_04  Bỏ trống Số điện thoại → cảnh báo
TC_CK_05  Bỏ trống Địa chỉ → cảnh báo
TC_CK_06  SĐT là chữ → cảnh báo định dạng
TC_CK_07  SĐT không bắt đầu 0 → cảnh báo
TC_CK_08  SĐT quá dài (> 11 ký tự) → cảnh báo
TC_CK_09  SĐT quá ngắn (< 10 ký tự) → cảnh báo
TC_CK_10  Chưa đăng nhập → nút thanh toán ẩn, link đăng nhập hiện
TC_CK_11  Dropdown thanh toán đủ 2 option (COD, Chuyển khoản)
TC_CK_12  Sau thanh toán → cart-counter = 0
TC_CK_13  Popup xác nhận xuất hiện trước khi đặt hàng
TC_CK_14  Cancel popup → đơn không tạo, vẫn ở /cart
TC_CK_15  Tổng tiền sau áp voucher hiển thị chính xác
TC_CK_16  DaSuDung của voucher tăng 1 sau thanh toán thành công
─────────────────────────────────────────────────────────────────────────────
"""

import time
import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from discounts.test.conftest import driver, cart_ready
from discounts.test.pages.EditVoucherPage import EditVoucherPage
from discounts.test.pages.HomePage import HomePage
from discounts.test.pages.LoginPage import LoginPage
from discounts.test.pages.PayPage import PayPage

BASE_URL   = "http://127.0.0.1:5000"
SS_SEARCH  = "discounts/test/screenshots/SearchVoucher"
SS_CK      = "discounts/test/screenshots/Checkout"

VALID_NAME    = "Nguyễn Văn A"
VALID_PHONE   = "0321277291"
VALID_ADDRESS = "Nhà Bè TPHCM"

def test_login_customer(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")
    time.sleep(1)

# ═══════════════════════════════════════════════════════════════════════════
#  MODULE 2 – THANH TOÁN
# ═══════════════════════════════════════════════════════════════════════════

def test_TC_CK_01_cod_khong_voucher(cart_ready):
    """Thanh toán COD không dùng voucher → thành công."""
    driver = cart_ready
    test_login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, VALID_PHONE, VALID_ADDRESS)
    page.select_payment("COD")
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("thành công" in m.lower() for m in msgs), \
        f"Không có thông báo thành công: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_01")


def test_TC_CK_02_chuyen_khoan_co_voucher(cart_ready):
    """Thanh toán Chuyển khoản + voucher → tổng tiền giảm, thành công."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.open_voucher()
    page.choose_voucher()
    time.sleep(1)

    assert page.get_discount_amount() != "0đ", \
        "Voucher chưa được áp dụng"

    page.enter_info(VALID_NAME, VALID_PHONE, VALID_ADDRESS)
    page.select_payment("Chuyển khoản")
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("thành công" in m.lower() for m in msgs), \
        f"Không có thông báo thành công: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_02")


def test_TC_CK_03_ten_nguoi_nhan_trong(cart_ready):
    """Bỏ trống Tên người nhận → cảnh báo."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info("", VALID_PHONE, VALID_ADDRESS)
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("tên" in m.lower() for m in msgs), \
        f"Không có cảnh báo tên: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_03")


def test_TC_CK_04_sdt_trong(cart_ready):
    """Bỏ trống SĐT → cảnh báo."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, "", VALID_ADDRESS)
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("điện thoại" in m.lower() for m in msgs), \
        f"Không có cảnh báo SĐT: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_04")


def test_TC_CK_05_dia_chi_trong(cart_ready):
    """Bỏ trống Địa chỉ → cảnh báo."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, VALID_PHONE, "")
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("địa chỉ" in m.lower() for m in msgs), \
        f"Không có cảnh báo địa chỉ: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_05")


def test_TC_CK_06_sdt_la_chu(cart_ready):
    """SĐT là chữ → cảnh báo định dạng."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, "abcde", VALID_ADDRESS)
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("điện thoại" in m.lower() for m in msgs), \
        f"Không có cảnh báo SĐT chữ: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_06")


def test_TC_CK_07_sdt_khong_bat_dau_0(cart_ready):
    """SĐT không bắt đầu bằng 0 → cảnh báo."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, "1234567890", VALID_ADDRESS)
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("điện thoại" in m.lower() for m in msgs), \
        f"Không có cảnh báo SĐT không bắt đầu 0: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_07")


def test_TC_CK_08_sdt_qua_dai(cart_ready):
    """SĐT > 11 ký tự → cảnh báo."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, "023456789011", VALID_ADDRESS)
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("điện thoại" in m.lower() for m in msgs), \
        f"Không có cảnh báo SĐT quá dài: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_08")


def test_TC_CK_09_sdt_qua_ngan(cart_ready):
    """SĐT < 10 ký tự → cảnh báo."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, "023456789", VALID_ADDRESS)
    page.checkout()

    msgs = page.get_all_alerts()
    assert any("điện thoại" in m.lower() for m in msgs), \
        f"Không có cảnh báo SĐT quá ngắn: {msgs}"
    _ss(driver, SS_CK, "actual_output_TC_CK_09")


def test_TC_CK_10_chua_dang_nhap(driver):
    """Chưa đăng nhập → nút Thanh toán ngay ẩn, link Đăng nhập hiện."""
    home = HomePage(driver=driver)
    home.open_page()
    home.add_to_cart()
    time.sleep(1)

    page = PayPage(driver=driver)
    page.open_page()

    assert not page.is_checkout_btn_visible(), \
        "Nút Thanh toán ngay không nên hiển thị khi chưa đăng nhập!"
    assert page.is_login_link_visible(), \
        "Link Đăng nhập không hiển thị"
    _ss(driver, SS_CK, "actual_output_TC_CK_10")


def test_TC_CK_11_dropdown_thanh_toan(driver):
    """Dropdown thanh toán có đúng 2 option: COD và Chuyển khoản."""
    home = HomePage(driver=driver)
    home.open_page()
    home.add_to_cart()
    time.sleep(1)

    page = PayPage(driver=driver)
    page.open_page()

    options = page.get_payment_options()
    assert any("COD" in o for o in options), \
        f"Không có option COD: {options}"
    assert any("Chuyển khoản" in o for o in options), \
        f"Không có option Chuyển khoản: {options}"
    _ss(driver, SS_CK, "actual_output_TC_CK_11")


def test_TC_CK_12_sau_thanh_toan_gio_hang_ve_0(cart_ready):
    """Sau thanh toán thành công → cart-counter = 0."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, VALID_PHONE, VALID_ADDRESS)
    page.checkout()
    page.get_all_alerts()

    page.wait_for_redirect("/")
    assert page.get_cart_counter() == "0", \
        f"Giỏ hàng chưa về 0: {page.get_cart_counter()}"
    _ss(driver, SS_CK, "actual_output_TC_CK_12")


def test_TC_CK_13_popup_xac_nhan_xuat_hien(cart_ready):
    """Nhấn Thanh toán ngay → popup xác nhận xuất hiện trước khi chốt."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, VALID_PHONE, VALID_ADDRESS)

    # Click nhưng KHÔNG accept – kiểm tra alert có xuất hiện không
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    driver.find_element(By.ID, "btn-checkout-now").click()
    time.sleep(1)

    has_alert = False
    try:
        from selenium.webdriver.common.alert import Alert
        alert = Alert(driver)
        _ = alert.text
        has_alert = True
        alert.dismiss()
    except Exception:
        # SweetAlert modal
        try:
            modal = driver.find_element(
                By.CSS_SELECTOR, ".swal2-popup, [role='dialog']"
            )
            has_alert = modal.is_displayed()
        except NoSuchElementException:
            pass

    assert has_alert, "Không xuất hiện popup xác nhận trước khi đặt hàng!"
    _ss(driver, SS_CK, "actual_output_TC_CK_13")


def test_TC_CK_14_cancel_popup_don_khong_tao(cart_ready):
    """Nhấn Cancel ở popup xác nhận → đơn không tạo, vẫn ở /cart."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.enter_info(VALID_NAME, VALID_PHONE, VALID_ADDRESS)
    page.checkout_and_cancel()

    assert "/cart" in driver.current_url, \
        f"Đơn đã tạo dù nhấn Cancel! URL: {driver.current_url}"
    assert len(page.get_cart_items()) > 0, \
        "Giỏ hàng trống dù không thanh toán"
    _ss(driver, SS_CK, "actual_output_TC_CK_14")


def test_TC_CK_15_tong_tien_sau_voucher(cart_ready):
    """Tổng tiền sau áp voucher = tổng gốc − giá trị giảm."""
    driver = cart_ready
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()

    def _parse(text: str) -> float:
        return float(
            text.replace("VNĐ", "").replace("đ", "")
                .replace(".", "").replace(",", "").replace("-", "")
                .strip()
        )

    original = _parse(page.get_total())

    page.open_voucher()
    page.choose_voucher()
    time.sleep(1)

    discount = _parse(page.get_discount_amount())
    new_total = _parse(page.get_total_new())

    assert discount > 0, "Voucher không tạo ra giảm giá"
    assert abs((original - discount) - new_total) < 1, \
        f"Tổng sai: {original} - {discount} ≠ {new_total}"
    _ss(driver, SS_CK, "actual_output_TC_CK_15")


def test_TC_CK_16_da_su_dung_tang_sau_thanh_toan(cart_ready):
    """DaSuDung của voucher tăng đúng 1 sau khi KH thanh toán thành công."""
    driver = cart_ready

    # Bước 1: Admin ghi nhận DaSuDung hiện tại
    _login_admin(driver)
    admin_page = EditVoucherPage(driver=driver)
    admin_page.open_admin()
    usage_before_text = admin_page.get_soluong_in_row(VOUCHER_EXACT)
    # usage_text dạng "N / SoLuong"
    da_su_dung_before = int(usage_before_text.split("/")[0].strip())

    # Bước 2: KH đặt hàng với voucher đó
    _login_customer(driver)

    page = PayPage(driver=driver)
    page.open_page()
    page.open_voucher()

    try:
        page.select_voucher_by_code(VOUCHER_EXACT)
    except Exception:
        page.choose_voucher()

    time.sleep(1)

    page.enter_info(VALID_NAME, VALID_PHONE, VALID_ADDRESS)
    page.checkout()
    page.get_all_alerts()
    page.wait_for_redirect("/")
    time.sleep(1)

    # Bước 3: Admin kiểm tra lại DaSuDung
    _login_admin(driver)
    admin_page.open_admin()
    usage_after_text = admin_page.get_soluong_in_row(VOUCHER_EXACT)
    da_su_dung_after = int(usage_after_text.split("/")[0].strip())

    assert da_su_dung_after == da_su_dung_before + 1, \
        f"DaSuDung không tăng: trước={da_su_dung_before}, sau={da_su_dung_after}"
    _ss(driver, SS_CK, "actual_output_TC_CK_16")
