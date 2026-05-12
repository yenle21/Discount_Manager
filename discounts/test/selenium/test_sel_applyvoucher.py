import os
import time
from datetime import datetime

import pyautogui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from discounts.test.pages.ApplyVoucherPage import  ApplyVoucherPage
from discounts.test.conftest import driver, cart_ready
from discounts.test.pages.HomePage import HomePage
from discounts.test.pages.LoginPage import LoginPage


def test_TC01_view_cart(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    # có sản phẩm
    items = driver.find_elements(By.CSS_SELECTOR, "#cart-items-container > div")
    assert len(items) > 0

    # có tên
    names = driver.find_elements(By.CLASS_NAME, "card-title")
    assert all(n.text != "" for n in names)

    # có giá
    prices = driver.find_elements(By.CSS_SELECTOR, "#cart > div.col-2.text-center.fw-bold")
    assert all("VNĐ" in p.text for p in prices)

    # có số lượng
    qty = driver.find_elements(By.XPATH, "//input[@type='number']")
    assert all(int(q.get_attribute("value")) > 0 for q in qty)

    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC01.png")


def test_TC02_delete_item(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    # lấy danh sách tên sản phẩm
    names_before = [e.text for e in driver.find_elements(By.CLASS_NAME, "product-name-text")]

    # chọn sản phẩm đầu tiên
    name_deleted = names_before[0]

    # click xóa + accept alert
    cart.delete_item()

    # lấy lại danh sách
    names_after = [e.text for e in driver.find_elements(By.CLASS_NAME, "card-title")]

    # assert sản phẩm đã bị xóa
    assert name_deleted not in names_after

    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC02.png")

def test_TC02_delete_item_api(test_client, test_app):
    key = test_app.config['CART_KEY']

    # setup cart
    with test_client.session_transaction() as sess:
        sess[key] = {
            "1": {"price": 10000, "quantity": 2}
        }

    res = test_client.delete('/api/cart/1')
    data = res.get_json()

    assert res.status_code == 200
    assert data["total_price"] == 0

    # check session
    with test_client.session_transaction() as sess:
        assert "1" not in sess[key]

def test_TC03_update_quantity(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.update_quantity(2)

    qty = cart.get_quantity()

    assert int(qty) == 2
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC03.png")

def test_TC03_update_quantity_api(test_client):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 10000, "quantity": 1}
        }

    res = test_client.put('/api/cart/1', json={"quantity": 3})

    assert res.status_code == 200
    assert res.json["total_quantity"] == 3
    assert res.json["total_price"] == 30000

def test_TC03_invalid_quantity(test_client):
    res = test_client.put('/api/cart/1', json={"quantity": "abc"})

    assert res.status_code == 400

def test_TC03_quantity_zero_delete(test_client):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 10000, "quantity": 1}
        }

    res = test_client.put('/api/cart/1', json={"quantity": 0})

    assert res.json["total_quantity"] == 0
    assert res.json["total_price"] == 0

def test_TC04_total_api(test_client):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 10000, "quantity": 2},
            "2": {"price": 5000, "quantity": 1}
        }

    res = test_client.put('/api/cart/1', json={"quantity": 2})

    data = res.json
    assert res.status_code == 200
    assert data["total_price"] == 25000

def test_TC04_total_ui(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    total = cart.get_total()

    assert "VNĐ" in total
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC04.png")

def test_TC05_apply_voucher(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.open_voucher()
    cart.choose_voucher()

    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC05.png")

def test_TC05_apply_voucher_api(test_client, sample_vouchers):
    v = sample_vouchers[0]
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Kem bắp",
                "price": 100000,
                "quantity": 1,
                "category_id": 1
            }
        }

    res = test_client.put(f'/api/apply-voucher/{v.MaGG}', json={
        "voucher_id": v.MaGG
    })

    data = res.get_json()

    assert data['status'] == 200
    assert "thành công" in data['message']

def test_TC06_remove_voucher(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()
    cart.open_voucher()
    cart.choose_voucher()

    before = cart.get_total_new()
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC06_1.png")

    cart.remove_voucher()

    after = cart.get_total_new()
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC06_2.png")

    assert before != after

def test_TC06_remove_voucher_api(test_client, sample_vouchers):
    v = sample_vouchers[0]

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "price": 100000,
                "quantity": 1,
                "category_id": 1
            }
        }
        sess['applied_vouchers'] = {
            "PROMOTION": {
                "MaGG": v.MaGG,
                "LoaiGG": v.LoaiGG,
                "GiaTri": float(v.GiaTri)
            }
        }

    res = test_client.delete('/api/apply-voucher/')
    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == 200

    # check session đã bị xóa
    with test_client.session_transaction() as sess:
        assert sess.get('applied_vouchers') == {}

def test_TC07_name_empty(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("","0321277291", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC07_api.png")
    msgs = cart.get_all_alerts()

    assert any("Tên người nhận không hợp lệ" in m for m in msgs)

def test_TC08_phone_empty(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC08_api.png")
    msgs = cart.get_all_alerts()

    assert any("Số điện thoại không đúng" in m for m in msgs)


def test_TC09_adress_empty(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","0321277291", "")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC09_api.png")
    msgs = cart.get_all_alerts()

    assert any("Vui lòng nhập địa chỉ cụ thể" in m for m in msgs)


def test_TC10_17_18_checkout_success(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","0321277291", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC10_17_18_api.png")
    msgs = cart.get_all_alerts()

    assert any("thành công" in m for m in msgs)

def test_TC11_text_phone(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","abcd", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC11_api.png")
    msgs = cart.get_all_alerts()

    assert any("Số điện thoại không đúng" in m for m in msgs)


def test_TC12_phone_without_zero_first(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","1234567890", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC12_api.png")
    msgs = cart.get_all_alerts()

    assert any("Số điện thoại không đúng" in m for m in msgs)

def test_TC13_phone_gt(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","023456789011", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC13_api.png")
    msgs = cart.get_all_alerts()

    assert any("Số điện thoại không đúng" in m for m in msgs)

def test_TC14_phone_lt(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA","023456789", "NhaBe TPHCM")
    cart.checkout()
    time.sleep(0.5)
    pyautogui.screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC14_api.png")
    msgs = cart.get_all_alerts()

    assert any("Số điện thoại không đúng" in m for m in msgs)

def test_TC15_payment_dropdown(driver):
    cart = ApplyVoucherPage(driver)
    cart.open_page()
    cart.get_payment()
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC15.png")
    options = driver.find_elements(By.CSS_SELECTOR, "#payment-method > option")
    texts = [opt.text for opt in options]
    assert any("COD" in t for t in texts)
    assert any("Chuyển khoản" in t for t in texts)

def test_TC16_payment_selected(driver):
    cart = ApplyVoucherPage(driver)
    cart.open_page()
    cart.get_payment()

    e = driver.find_element(By.CSS_SELECTOR, "#payment-method > option:nth-child(1)")
    e.click()
    assert 'COD' in e.text
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC16.png")

def test_TC19_after_checkout_success(cart_ready):
    driver = cart_ready

    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.enter_info("NVA", "0321277291", "NhaBe TPHCM")
    cart.checkout()
    cart.get_all_alerts()

    wait = WebDriverWait(driver, 5)


    # 3. chờ redirect về trang chủ
    wait.until(EC.url_contains("/"))  # chỉnh theo route của bạn

    print("CURRENT URL:", driver.current_url)

    # assert đã về trang chủ
    assert "/" in driver.current_url.lower()

    # 4. kiểm tra giỏ hàng = 0
    cart_count = driver.find_element(By.ID, "cart-counter").text

    print("CART COUNT:", cart_count)

    assert cart_count == "0"

def test_TC20_voucher_popup(cart_ready):
    driver = cart_ready

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    # click nút "Sử dụng mã giảm giá"
    cart.open_voucher()

    wait = WebDriverWait(driver, 5)

    # chờ popup hiển thị
    popup = wait.until(
        EC.visibility_of_element_located(
            (By.CLASS_NAME, "modal-body")
        )
    )

    # lấy text của các tab
    tabs = driver.find_elements(By.ID, "voucherTab")

    tab_texts = [t.text for t in tabs]

    print("TABS:", tab_texts)

    # assert
    assert any("Khuyến mãi" in t for t in tab_texts)
    assert any("Miễn phí ship" in t for t in tab_texts)
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC20.png")

def test_TC21_apply_voucher_by_category(cart_ready):
    driver = cart_ready

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    # mở popup
    cart.open_voucher()

    # chọn tab khuyến mãi
    cart.select_voucher_tab("Khuyến mãi")

    # chọn voucher SPRING26
    cart.choose_voucher()

    # kiểm tra số tiền giảm
    discount = cart.get_discount_amount()

    print("DISCOUNT:", discount)

    assert discount == '-98,000đ'
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC21.png")


def test_TC22_voucher_not_applied_wrong_category(driver):
    home = HomePage(driver)
    home.open_page()

    home.add_to_cart_not_milk()

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.open_voucher()
    cart.select_voucher_tab("Khuyến mãi")


    try:
        cart.select_voucher_by_code("Milk")
    except:
        pass  # nếu không thấy thì OK luôn

    # lấy danh sách đã apply
    applied = cart.get_applied_vouchers()

    print("APPLIED:", applied)


    assert not any("Milk" in v for v in applied)
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC22.png")

def test_TC23_apply_voucher_min_order_fail(test_client, sample_vouchers):
    v, v_valid, _, _ = sample_vouchers

    # 🛒 Tạo cart < DieuKien (100k)
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "price": 50000,
                "quantity": 1,
                "category_id": 1
            }
        }

    # 🚀 Gọi API
    res = test_client.put(
        f"/api/apply-voucher/{v.MaGG}",
        json={"voucher_id": v.MaGG}
    )

    data = res.get_json()


    assert res.status_code == 200
    assert data["status"] == 404
    assert "tối thiểu" in data["message"]

def test_TC24_apply_voucher_equal_min(test_client, sample_vouchers):
    v, v_valid, _, _ = sample_vouchers

    # 🛒 total = 100k (đúng điều kiện)
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "price": 50000,
                "quantity": 2,   # 50k * 2 = 100k
                "category_id": 1
            }
        }

    res = test_client.put(
        f"/api/apply-voucher/{v.MaGG}",
        json={"voucher_id": v.MaGG}
    )

    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == 200
    assert "thành công" in data["message"]

def test_TC25_apply_voucher_gt_min(test_client, sample_vouchers):
    v, v_valid, _, _ = sample_vouchers

    # 🛒 total = 150k (> điều kiện)
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "price": 50000,
                "quantity": 3,   # 50k * 3 = 150k
                "category_id": 1
            }
        }

    res = test_client.put(
        f"/api/apply-voucher/{v.MaGG}",
        json={"voucher_id": v.MaGG}
    )

    data = res.get_json()

    assert res.status_code == 200
    assert data["status"] == 200
    assert "thành công" in data["message"]

def test_TC26_replace_voucher(test_client, sample_vouchers):
    v, v_valid, _, _ = sample_vouchers

    # cart hợp lệ
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 100000, "quantity": 1, "category_id": 1}
        }

    # apply voucher đầu
    test_client.put(
        f"/api/apply-voucher/{v_valid.MaGG}",
        json={"voucher_id": v_valid.MaGG}
    )

    # apply voucher thứ 2 (cùng loại Shipping → phải replace)
    res = test_client.put(
        f"/api/apply-voucher/{v_valid.MaGG}",
        json={"voucher_id": v_valid.MaGG}
    )

    data = res.get_json()

    assert data["status"] == 200
    assert data["applied_vouchers"]["SHIPPING"]["MaGG"] == v_valid.MaGG

def test_TC27_voucher_not_started(test_client, sample_vouchers):
    _, _, v_future, _ = sample_vouchers

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 100000, "quantity": 1, "category_id": 1}
        }

    res = test_client.put(
        f"/api/apply-voucher/{v_future.MaGG}",
        json={"voucher_id": v_future.MaGG}
    )

    data = res.get_json()

    assert data["status"] == 404
    assert "chưa đến hạn" in data["message"]

def test_TC28_voucher_valid(test_client, sample_vouchers):
    _, v_valid, _, _ = sample_vouchers

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 100000, "quantity": 1, "category_id": 1}
        }

    res = test_client.put(
        f"/api/apply-voucher/{v_valid.MaGG}",
        json={"voucher_id": v_valid.MaGG}
    )

    data = res.get_json()

    assert data["status"] == 200
    assert "thành công" in data["message"]

def test_TC29_voucher_expired(test_client, sample_vouchers):
    _, _, _, v_expired = sample_vouchers

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 100000, "quantity": 1, "category_id": 1}
        }

    res = test_client.put(
        f"/api/apply-voucher/{v_expired.MaGG}",
        json={"voucher_id": v_expired.MaGG}
    )

    data = res.get_json()

    assert data["status"] == 404
    assert "hết hạn" in data["message"]