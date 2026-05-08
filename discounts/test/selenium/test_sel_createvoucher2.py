import time
from datetime import datetime
from selenium.webdriver.common.by import By
from discounts.test.pages.CreateVoucherPage2 import CreateVoucherPage2
from discounts.test.pages.LoginPage import LoginPage

BASE_URL   = "http://127.0.0.1:5000"
CREATE_URL = f"{BASE_URL}/create"
ADMIN_URL  = f"{BASE_URL}/admin"
LOGIN_URL  = f"{BASE_URL}/login"

# Tham số mặc định
VALID = dict(
    hinhthuc="Mã khuyến mãi",
    loaigg="Giảm theo số tiền",
    giatri="20000000",
    soluong="1",
    ngaybd_date="06052026", ngaybd_time="1000A",
    ngaykt_date="07052026", ngaykt_time="0906P",
    mota="Voucher test tự động",
    dieukiensp="-- Tất cả sản phẩm --",
    tientoithieu="500000",
)

def _login_admin(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Quản Trị Viên", "admin", "123")
    time.sleep(1)

def _login_customer(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")
    time.sleep(1)

def _create(driver, **kwargs) -> CreateVoucherPage2:
    page = CreateVoucherPage2(driver=driver)
    page.open_page()
    page.createvoucher(**kwargs)
    return page

# TEST QUYỀN TRUY CẬP

def test_TC_CV_01_admin_tao_voucher_thanh_cong(driver):
    _login_admin(driver)
    magg = "SPRING26"
    page = _create(driver, magg= magg, **VALID)
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    row = page.get_row_by_magg(magg)
    assert row is not None

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_01")

def test_TC_CV_02_khach_hang_khong_truy_cap_duoc(driver):
    _login_customer(driver)
    page = CreateVoucherPage2(driver=driver)
    page.open_page()

    assert driver.current_url == f"{BASE_URL}/"
    assert "Không có quyền truy cập" in page.get_alert_text()

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_02")

def test_TC_CV_03_chua_dang_nhap(driver):
    page = CreateVoucherPage2(driver=driver)
    page.open_page()

    assert driver.current_url == f"{BASE_URL}/login"
    assert "Không có quyền truy cập" in page.get_alert_text()

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_03")

# TEST TẠO VOUCHER THÀNH CÔNG

def test_TC_CV_04_hinhthuc_shipping(driver):
    _login_admin(driver)
    magg = "FREESHIP20"
    page = _create(driver, magg=magg, **{**VALID, "hinhthuc": "Miễn phí Ship"})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    badge = page.get_hinhthuc_badge_in_row(magg)
    assert badge == "Shipping"

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_04")

def test_TC_CV_05_hinhthuc_khuyenmai(driver):
    _login_admin(driver)
    magg = "DELETE"
    page = _create(driver, magg=magg, **VALID)
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    badge = page.get_hinhthuc_badge_in_row(magg)
    assert badge == "Khuyến mãi"

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_05")

def test_TC_CV_06_trangthai_pending(driver):
    _login_admin(driver)
    magg = "PENDING"
    page = _create(driver, magg=magg, **{**VALID, "ngaybd_date": "09052026"})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    status = page.get_status_in_row(magg)
    assert "pending" in status

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_06")

def test_TC_CV_07_trangthai_active(driver):
    _login_admin(driver)
    magg = "HETHAN"
    page = _create(driver, magg=magg, **{**VALID, "ngaybd_date": "05052026"})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    status = page.get_status_in_row(magg)
    assert "active" in status

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_07")

def test_TC_CV_08_trangthai_active(driver):
    _login_admin(driver)
    magg = "HETLUOT"
    page = _create(driver, magg=magg,
                   **{**VALID, "ngaybd_date": "06052026", "ngaybd_time": "0902P"})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    status = page.get_status_in_row(magg)
    assert "active" in status

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_08")

def test_TC_CV_09_dieukien_sanpham(driver):
    _login_admin(driver)
    magg = "DKSP"
    page = _create(driver, magg=magg, **{**VALID, "dieukiensp": "Sữa"})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    row = page.get_row_by_magg(magg)
    assert row is not None
    assert "Sữa" in row.text

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_09")

def test_TC_CV_10_khong_diekien_giatri(driver):
    _login_admin(driver)
    magg = "NODKGT"
    page = _create(driver, magg=magg, **{**VALID, "tientoithieu": ""})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    row = page.get_row_by_magg(magg)
    assert row is not None
    assert "0 VNĐ" in row.text

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_10")

def test_TC_CV_11_khong_mota(driver):
    _login_admin(driver)
    magg = "NOMOTA"
    page = _create(driver, magg=magg, **{**VALID, "mota": ""})
    page.click_save()

    assert driver.current_url == ADMIN_URL
    assert "thành công" in page.get_alert_text()
    mota = page.get_mota_in_row(magg)
    assert "Không có mô tả" in mota

    driver.execute_script("window.scrollTo(0,250)")
    time.sleep(1)
    page.screenshot("actual_output_TC_CV_11")

# TEST TẠO VOUCHER KHÔNG THÀNH CÔNG

# MÃ GIẢM GIÁ

def test_TC_CV_12_magg_trong(driver):
    _login_admin(driver)
    page = _create(driver, magg="", **VALID)
    page.click_save()

    alert = page.get_alert_text()
    assert "Vui lòng nhập Mã Voucher!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_12")

def test_TC_CV_13_magg_trung(driver):
    _login_admin(driver)

    page = _create(driver, magg="TRUNGMA", **VALID)
    page.click_save()
    time.sleep(1)

    page = _create(driver, magg="TRUNGMA", **VALID)
    page.click_save()

    alert = page.get_alert_text()
    assert "Mã voucher đã tồn tại!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_13")

def test_TC_CV_14_magg_ky_tu_dac_biet(driver):
    _login_admin(driver)
    page = _create(driver, magg="KYTUDB@", **VALID)
    page.click_save()

    msg = page.get_magg_validation_message()
    assert "Please match the requested format" in msg
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_14")

def test_TC_CV_15_magg_co_khoang_trang(driver):
    _login_admin(driver)
    page = _create(driver, magg="KHOANG TRANG", **VALID)
    page.click_save()

    msg = page.get_magg_validation_message()
    assert "Please match the requested format" in msg
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_15")

def test_TC_CV_16_magg_hon_15_ky_tu(driver):
    _login_admin(driver)
    page = _create(driver, magg="MAGGDAIHON15KYTU", **VALID)

    actual = page.get_magg_value()
    assert len(actual) <= 15

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_16")

def test_TC_CV_17_magg_trung_chu_hoa_thuong(driver):
    _login_admin(driver)
    page = _create(driver, magg="TRUNGHOATHUONG", **VALID)
    page.click_save()
    time.sleep(1)

    page = _create(driver, magg="trunghoathuong", **VALID)
    page.click_save()

    alert = page.get_alert_text()
    assert "Mã voucher đã tồn tại!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_17")

# GIÁ TRỊ GIẢM

def test_TC_CV_18_giatri_trong_so_tien(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRITRONGVND", **{**VALID, "loaigg": "Giảm theo số tiền", "giatri": ""})
    page.click_save()

    alert = page.get_alert_text()
    assert "Sai định dạng dữ liệu!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_18")

def test_TC_CV_19_giatri_trong_phan_tram(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRITRONGPT",
                   **{**VALID, "loaigg": "Giảm theo %", "giatri": ""})
    page.click_save()

    alert = page.get_alert_text()
    assert "Sai định dạng dữ liệu!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_19")

def test_TC_CV_20_giatri_bang_0_so_tien(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRI0VND",
                   **{**VALID, "loaigg": "Giảm theo số tiền", "giatri": "0"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Giá trị giảm phải lớn hơn 0!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_20")

def test_TC_CV_21_giatri_bang_0_phan_tram(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRI0PT",
                   **{**VALID, "loaigg": "Giảm theo %", "giatri": "0"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Giá trị giảm phải lớn hơn 0!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_21")

def test_TC_CV_22_giatri_am_so_tien(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRIAMVND",
                   **{**VALID, "loaigg": "Giảm theo số tiền", "giatri": "-1"})

    actual = page.get_giatri_value()
    assert actual == "0"
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_22")

def test_TC_CV_23_giatri_am_phan_tram(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRIAMPT",
                   **{**VALID, "loaigg": "Giảm theo %", "giatri": "-1"})

    actual = page.get_giatri_value()
    assert actual == "0"
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_23")

def test_TC_CV_24_giatri_lon_hon_50_phan_tram(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRIHON50PT",
                   **{**VALID, "loaigg": "Giảm theo %", "giatri": "51"})

    actual = page.get_giatri_value()
    assert actual == "50"
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_24")

def test_TC_CV_25_giatri_hon_20tr_loai_tien(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRIHON20TR",
                   **{**VALID, "loaigg": "Giảm theo số tiền", "giatri": "20000001"})

    actual = page.get_giatri_value()
    assert actual == "20000000"
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_25")

def test_TC_CV_26_giatri_chu_so_tien(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRICHUVND",
                   **{**VALID, "loaigg": "Giảm theo số tiền", "giatri": "chữ"})

    actual = page.get_giatri_value()
    assert actual == ""
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_26")

def test_TC_CV_27_giatri_chu_phan_tram(driver):
    _login_admin(driver)
    page = _create(driver, magg="GIATRICHUPT",
                   **{**VALID, "loaigg": "Giảm theo %", "giatri": "chữ"})

    actual = page.get_giatri_value()
    assert actual == ""
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_27")

#  SỐ LƯỢNG

def test_TC_CV_28_soluong_trong(driver):
    _login_admin(driver)
    page = _create(driver, magg="SLTRONG", **{**VALID, "soluong": ""})
    page.click_save()

    msg = page.get_soluong_validation_message()
    assert "Please fill out this field." in msg
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_28")

def test_TC_CV_29_soluong_0(driver):
    _login_admin(driver)
    page = _create(driver, magg="SL0", **{**VALID, "soluong": "0"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Số lượng không hợp lệ!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_29")

def test_TC_CV_30_soluong_am(driver):
    _login_admin(driver)
    page = _create(driver, magg="SLAM", **{**VALID, "soluong": "-1"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Số lượng không hợp lệ!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_30")

def test_TC_CV_31_soluong_chu(driver):
    _login_admin(driver)
    page = _create(driver, magg="SLCHU", **{**VALID, "soluong": "chữ"})

    actual = page.get_soluong_value()
    assert actual == ""
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_31")

def test_TC_CV_32_soluong_thap_phan(driver):
    _login_admin(driver)
    page = _create(driver, magg="SLTHAPPHAN", **{**VALID, "soluong": "1.1"})
    page.click_save()

    msg = page.get_soluong_validation_message()
    assert "Please enter a valid value." in msg
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_32")

def test_TC_CV_33_soluong_hon_1000(driver):
    _login_admin(driver)
    page = _create(driver, magg="SLHON1000", **{**VALID, "soluong": "1001"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Số lượng không hợp lệ!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_33")

#  NGÀY (NgayBD / NgayKT)

def test_TC_CV_34_ngaybd_trong(driver):
    _login_admin(driver)
    page = _create(driver, magg="NGAYBDTRONG",
                   **{**VALID, "ngaybd_date": None, "ngaybd_time": None})
    page.click_save()

    msg = page.get_ngaybd_validation_message()
    assert "Please fill out this field." in msg
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_34")

def test_TC_CV_35_ngaykt_trong(driver):
    _login_admin(driver)
    page = _create(driver, magg="NGAYKTTRONG",
                   **{**VALID, "ngaykt_date": None, "ngaykt_time": None})
    page.click_save()

    msg = page.get_ngaykt_validation_message()
    assert "Please fill out this field." in msg
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_35")

def test_TC_CV_36_ngaykt_nho_hon_ngaybd(driver):
    _login_admin(driver)
    page = _create(driver, magg="KTNHOHONBD",
                   **{**VALID, "ngaybd_date": "10052026", "ngaykt_date": "01052026"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_36")

def test_TC_CV_37_ngaykt_bang_ngaybd(driver):
    _login_admin(driver)
    page = _create(driver, magg="KTBANGBD",
                   **{**VALID,
                      "ngaybd_date": "10052026", "ngaybd_time": "1010A",
                      "ngaykt_date": "10052026", "ngaykt_time": "1010A"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_37")

def test_TC_CV_38_ngaykt_nho_hon_ngayhientai(driver):
    _login_admin(driver)
    page = _create(driver, magg="KTNHOHONHIENTAI",
                   **{**VALID, "ngaybd_date": "10042026", "ngaykt_date": "01052026"})
    page.click_save()

    alert = page.get_alert_text()
    assert "Ngày kết thúc không hợp lệ!" in alert
    assert driver.current_url == CREATE_URL

    time.sleep(1)
    page.screenshot("actual_output_TC_CV_38")
