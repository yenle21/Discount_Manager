import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from discounts.test.conftest import driver
from discounts.test.pages.EditVoucherPage import EditVoucherPage
from discounts.test.pages.LoginPage import LoginPage

BASE_URL   = "http://127.0.0.1:5000"

VOUCHER_EXACT   = "SPRING26"
VOUCHER_PARTIAL = "SPRING"
VOUCHER_LOWERCASE = "s"
VOUCHER_NONE    = "NOTEXIST"
VOUCHER_UNUSED = "SPRING26"
VOUCHER_USED   = "FREESHIP20"
VOUCHER_DELETE = "DELETE"
VOUCHER_EXPIRED = "HETHAN"
VOUCHER_FULL = "HETLUOT"

def _login_admin(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    time.sleep(1)

def _search(driver, keyword: str):
    box = driver.find_element(By.CSS_SELECTOR, "input[name='kw']")
    box.clear()
    box.send_keys(keyword)
    box.submit()
    time.sleep(1)

def _select_trang_thai(driver, value: str):
    sel = Select(driver.find_element(By.CSS_SELECTOR, "select[name='trang_thai']"))
    sel.select_by_value(value)
    time.sleep(1)

def _select_hinh_thuc(driver, value: str):
    sel = Select(driver.find_element(By.CSS_SELECTOR, "select[name='hinh_thuc']"))
    sel.select_by_value(value)
    time.sleep(1)

def _rows(driver):
    return driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

#  TEST TÌM KIẾM VOUCHER

def test_TC_SEARCH_01_tim_dung_ma(driver):
    _login_admin(driver)

    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _search(driver, VOUCHER_EXACT)

    rows = _rows(driver)
    assert len(rows) >= 1
    assert any(VOUCHER_EXACT in r.text for r in rows)
    page.screenshot("actual_output_TC_SEARCH_01")
def test_TC_SEARCH_02_tim_chuoi_con(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _search(driver, VOUCHER_PARTIAL)

    rows = _rows(driver)
    assert len(rows) >= 1
    for r in rows:
        assert VOUCHER_PARTIAL.lower() in r.text.lower()
    page.screenshot("actual_output_TC_SEARCH_02")

def test_TC_SEARCH_03_tim_chu_in_thuong(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _search(driver, VOUCHER_LOWERCASE)

    rows = _rows(driver)
    assert len(rows) >= 1
    page.screenshot("actual_output_TC_SEARCH_03")

def test_TC_SEARCH_04_tim_khong_nhap(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()

    total_rows = len(_rows(driver))

    _search(driver, "")
    rows_after = _rows(driver)
    assert len(rows_after) == total_rows
    page.screenshot("actual_output_TC_SEARCH_04")

def test_TC_SEARCH_05_tim_khong_ton_tai(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _search(driver, VOUCHER_NONE)

    rows = _rows(driver)
    assert len(rows) == 0
    page.screenshot("actual_output_TC_SEARCH_05")

def test_TC_SEARCH_06_loc_trang_thai_active(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _select_trang_thai(driver, "Active")
    page.screenshot("actual_output_TC_SEARCH_06")

    rows = _rows(driver)
    assert len(rows) >= 1
    for r in rows:
        badges = r.find_elements(By.CSS_SELECTOR, ".status-badge")
        assert any("active" in b.text.lower() for b in badges)
    page.screenshot("actual_output_TC_SEARCH_06")

def test_TC_SEARCH_07_loc_trang_thai_pending(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _select_trang_thai(driver, "pending")

    rows = _rows(driver)
    assert len(rows) >= 1
    for r in rows:
        badges = r.find_elements(By.CSS_SELECTOR, ".status-badge")
        assert any("pending" in b.text.lower() for b in badges)
    page.screenshot("actual_output_TC_SEARCH_07")

def test_TC_SEARCH_08_loc_trang_thai_expired(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _select_trang_thai(driver, "expired")

    rows = _rows(driver)
    assert len(rows) >= 1
    for r in rows:
        badges = r.find_elements(By.CSS_SELECTOR, ".status-badge")
        assert any("expired" in b.text.lower() for b in badges)
    page.screenshot("actual_output_TC_SEARCH_08")

def test_TC_SEARCH_09_tat_ca_trang_thai(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    total = len(_rows(driver))

    # Lọc bất kỳ
    _select_trang_thai(driver, "pending")
    time.sleep(1)

    # Đặt lại
    _select_trang_thai(driver, "")
    rows_after = _rows(driver)
    assert len(rows_after) == total
    page.screenshot("actual_output_TC_SEARCH_09")

def test_TC_SEARCH_10_loc_hinh_thuc_khuyenmai(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _select_hinh_thuc(driver, "Khuyến mãi")

    rows = _rows(driver)
    assert len(rows) >= 1
    for r in rows:
        badges = r.find_elements(By.CSS_SELECTOR, ".badge.bg-danger")
        assert len(badges) > 0
    page.screenshot("actual_output_TC_SEARCH_10")

def test_TC_SEARCH_11_loc_hinh_thuc_shipping(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    _select_hinh_thuc(driver, "Shipping")

    rows = _rows(driver)
    assert len(rows) >= 1
    for r in rows:
        badges = r.find_elements(By.CSS_SELECTOR, ".badge.bg-success")
        assert len(badges) > 0
    page.screenshot("actual_output_TC_SEARCH_11")

def test_TC_SEARCH_12_tat_ca_hinh_thuc(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    total = len(_rows(driver))

    # Lọc bất kỳ
    _select_hinh_thuc(driver, "Khuyến mãi")
    time.sleep(1)

    # Đặt lại
    _select_hinh_thuc(driver, "")
    rows_after = _rows(driver)
    assert len(rows_after) == total
    page.screenshot("actual_output_TC_SEARCH_12")

# TEST SỬA VOUCHER THÀNH CÔNG

def test_TC_EDIT_13_sua_hinhthuc_thanh_shipping(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(hinhthuc="Miễn phí Ship")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    badge = page.get_hinhthuc_badge_in_row(VOUCHER_UNUSED)
    assert badge == "Shipping"

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_13")

def test_TC_EDIT_14_sua_hinhthuc_thanh_khuyenmai(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(hinhthuc="Mã khuyến mãi")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    badge = page.get_hinhthuc_badge_in_row(VOUCHER_UNUSED)
    assert badge == "Khuyến mãi"

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_14")

def test_TC_EDIT_15_sua_loaigg_thanh_phantram(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(loaigg="Giảm theo %", giatri="20")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_15")

def test_TC_EDIT_16_sua_loaigg_thanh_sotien(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(loaigg="Giảm theo số tiền", giatri="10000")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_16")

def test_TC_EDIT_17_sua_trangthai_thanh_inactive(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(trangthai="inactive")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    status = page.get_status_in_row(VOUCHER_UNUSED)
    assert "pending" in status

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_17")

def test_TC_EDIT_18_sua_trangthai_thanh_active(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(trangthai="active")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    status = page.get_status_in_row(VOUCHER_UNUSED)
    assert "active" in status

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_18")

def test_TC_EDIT_19_sua_soluong(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)
    page.edit_voucher(soluong="350")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    quantity = page.get_soluong_in_row(VOUCHER_UNUSED)
    assert "350" in quantity

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_19")

def test_TC_EDIT_20_sua_ngaybd(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(
        ngaybd_date="03052026",
        ngaybd_time="1150P",
    )

    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    ngaybd = page.get_ngaybd_in_row(VOUCHER_UNUSED)
    assert "03/05/2026" in ngaybd
    assert "23:50" in ngaybd

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_20")

def test_TC_EDIT_21_sua_ngaykt(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(
        ngaykt_date="23052026",
        ngaykt_time="1150P",
    )

    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    ngaykt = page.get_ngaykt_in_row(VOUCHER_UNUSED)
    assert "23/05/2026" in ngaykt
    assert "23:50" in ngaykt

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_21")

def test_TC_EDIT_22_sua_mota(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    new_mota = "Test thay đổi mô tả"
    page.edit_voucher(mota=new_mota)
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()
    mota = page.get_mota_in_row(VOUCHER_UNUSED)
    assert new_mota in mota

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_22")

def test_TC_EDIT_23_sua_dieukiensp(driver):
    _login_admin(driver)

    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(dieukiensp="Sữa")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    row = page.get_row_by_magg(VOUCHER_UNUSED)
    assert row is not None
    assert "Sữa" in row.text

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_23")


def test_TC_EDIT_24_sua_dieukien_giatri(driver):
    _login_admin(driver)

    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(tientoithieu="200000")
    page.click_save()

    assert driver.current_url == f"{BASE_URL}/admin"
    assert "thành công" in page.get_alert_text().lower()

    row = page.get_row_by_magg(VOUCHER_UNUSED)
    assert row is not None
    assert "200.000 VNĐ" in row.text

    driver.execute_script("window.scrollTo(0, 250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_24")

# TEST SỬA VOUCHER KHÔNG THÀNH CÔNG

def test_TC_EDIT_25_magg_readonly(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    assert page.is_magg_readonly()
    page.screenshot("actual_output_TC_EDIT_25")

def test_TC_EDIT_26_huy_bo(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    old_mota = page.get_mota_value()

    page.edit_voucher(mota="Hủy bỏ thay đổi")
    page.click_cancel()

    assert driver.current_url == f"{BASE_URL}/admin"
    new_mota = page.get_mota_in_row(VOUCHER_UNUSED)
    assert new_mota == old_mota

    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_26")


def test_TC_EDIT_27_ngaykt_nho_hon_ngaybd(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(
        ngaybd_date="22052026", ngaybd_time="1000A",
        ngaykt_date="12052026", ngaykt_time="1000A",
    )
    page.click_save()

    assert driver.current_url != f"{BASE_URL}/admin"
    alert = page.get_alert_text()
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu!" in alert

    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_27")

def test_TC_EDIT_28_ngaykt_nho_hon_ngayhientai(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(
        ngaybd_date="22042026", ngaybd_time="1000A",
        ngaykt_date="02052026", ngaykt_time="1000A",
    )
    page.click_save()

    assert driver.current_url != f"{BASE_URL}/admin"
    alert = page.get_alert_text()
    assert "Ngày kết thúc không được ở quá khứ!" in alert

    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_28")

def test_TC_EDIT_29_giatrigiam_bang_0(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(giatri="0")
    page.click_save()

    assert driver.current_url != f"{BASE_URL}/admin"
    alert = page.get_alert_text()
    assert "Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ" in alert

    time.sleep(1)
    page.screenshot("actual_output_TC_EDIT_29")

def test_TC_EDIT_30_giatrigiam_hon_50_phantram(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(loaigg="Giảm theo %", giatri="100")

    actual = page.get_giatri_value()
    assert int(float(actual)) == 50

    page.screenshot("actual_output_TC_EDIT_30")

def test_TC_EDIT_31_soluong_bang_0(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_edit(VOUCHER_UNUSED)

    page.edit_voucher(soluong="0")
    page.click_save()

    assert driver.current_url != f"{BASE_URL}/admin"
    alert = page.get_alert_text()
    assert "Số lượng phát hành không hợp lệ" in alert
    page.screenshot("actual_output_TC_EDIT_31")

# TEST XÓA VOUCHER THÀNH CÔNG

def test_TC_DEL_32_xoa_voucher_chua_dung(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()
    page.click_delete_voucher(VOUCHER_DELETE)

    alert = page.get_alert_text()
    assert f"Xóa thành công voucher {VOUCHER_DELETE}!" in alert

    time.sleep(1)
    page.screenshot("actual_output_TC_DEL_32")

    page.open_admin()
    row = page.get_row_by_magg(VOUCHER_DELETE)
    assert row is None

def test_TC_DEL_33_xoa_voucher_chua_dung_het_han(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()

    page.click_delete_voucher(VOUCHER_EXPIRED)
    alert = page.get_alert_text()
    assert f"Voucher {VOUCHER_EXPIRED} đã hết hạn và đã được xóa!" in alert

    time.sleep(1)
    page.screenshot("actual_output_TC_DEL_33")

    page.open_admin()
    row = page.get_row_by_magg(VOUCHER_EXPIRED)
    assert row is None

def test_TC_DEL_34_xoa_voucher_het_so_luong(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()

    page.click_delete_voucher(VOUCHER_FULL)

    time.sleep(1)
    page.screenshot("actual_output_TC_DEL_34")

    alert = page.get_alert_text()
    assert f"Xóa thành công voucher {VOUCHER_FULL}!" in alert

    row = page.get_row_by_magg(VOUCHER_FULL)
    assert row is None

# TEST XÓA VOUCHER KHÔNG THÀNH CÔNG

def test_TC_DEL_35_xoa_voucher_da_dung_bi_khoa(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()

    row = page.get_row_by_magg(VOUCHER_USED)
    assert row is not None

    # Nút xóa phải bị disabled
    btn = row.find_element(By.CSS_SELECTOR, "button.btn-icon.delete")
    assert btn.get_attribute("disabled") is not None

    # Icon phải là fa-lock
    icon = btn.find_element(By.TAG_NAME, "i")
    assert "fa-lock" in icon.get_attribute("class")

    time.sleep(1)
    page.screenshot("actual_output_TC_DEL_35")

def test_TC_DEL_36_huy_xoa_voucher(driver):
    _login_admin(driver)
    page = EditVoucherPage(driver=driver)
    page.open_admin()

    page.click_delete_voucher_cancel(VOUCHER_UNUSED)

    assert driver.current_url == f"{BASE_URL}/admin"
    row = page.get_row_by_magg(VOUCHER_UNUSED)
    assert row is not None

    time.sleep(1)
    page.screenshot("actual_output_TC_DEL_36")
