import os
import time
from datetime import datetime
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

def test_TC03_update_quantity(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.update_quantity(2)

    qty = cart.get_quantity()

    assert int(qty) == 2
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC03.png")

def test_TC03_update_quantity_api(client):
    with client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 10000, "quantity": 1}
        }

    res = client.put('/api/cart/1', json={"quantity": 3})

    assert res.status_code == 200
    assert res.json["cart"]["1"]["quantity"] == 3

def test_TC03_invalid_quantity(client):
    res = client.put('/api/cart/1', json={"quantity": "abc"})

    assert res.status_code == 400

def test_TC03_quantity_zero_delete(client):
    with client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 10000, "quantity": 1}
        }

    res = client.put('/api/cart/1', json={"quantity": 0})

    assert "1" not in res.json["cart"]

def test_TC04_total_api(client):
    with client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"price": 10000, "quantity": 2},
            "2": {"price": 5000, "quantity": 1}
        }

    res = client.put('/api/cart/1', json={"quantity": 2})

    data = res.json
    cart = data["cart"]

    total_expected = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    assert data["total_amount"] == total_expected

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

def test_TC05_apply_voucher_api(test_client):
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

    res = test_client.put('/api/apply-voucher/1', json={
        "voucher_id": "sale10"
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

def test_TC06_remove_voucher_api(test_client):
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
        sess['voucher'] = "sale10"

    res = test_client.delete('/api/apply-voucher')

    data = res.get_json()

    # HTTP
    assert res.status_code == 200

    # response đúng format hiện tại
    assert data['status'] == 200
    assert 'total_price' in data
    assert 'message' in data

    # session đã bị clear
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

    assert discount == '-10,000đ'
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC21.png")


def test_TC22_voucher_not_applied_wrong_category(driver):
    home = HomePage(driver)
    home.open_page()

    home.add_to_cart_not_milk()

    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.open_voucher()
    cart.select_voucher_tab("Khuyến mãi")

    # thử chọn voucher SPRING26
    try:
        cart.select_voucher_by_code("Milk")
    except:
        pass  # nếu không thấy thì OK luôn

    # lấy danh sách đã apply
    applied = cart.get_applied_vouchers()

    print("APPLIED:", applied)

    # ❌ không được xuất hiện
    assert not any("Milk" in v for v in applied)
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC22.png")

def test_TC23_min_order_not_met(test_client):
    # Giỏ hàng < 100k
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Kem bắp",
                "price": 50000,
                "quantity": 1,
                "category_id": 3
            }
        }
        sess['applied_vouchers'] = {}

    res = test_client.put('/api/apply-voucher/1', json={
        "voucher_id": "SUM2026"
    })

    data = res.get_json()
    print("TC23:", data)

    # ❌ Không cho áp dụng
    assert data['status'] in [400, 422]
    assert "chưa đủ" in data['message'].lower() or "tối thiểu" in data['message'].lower()

    # ✔ Không lưu vào session
    with test_client.session_transaction() as sess:
        assert sess.get("applied_vouchers") == {}


def test_add_to_cart_success(test_client, app):
    key = app.config['CART_KEY']

    res = test_client.post("/api/cart", json={
        "id": 1,
        "name": "Sữa tươi",
        "price": 50000,
        "image": "milk.jpg",
        "category_id": 2
    })

    data = res.get_json()
    print("RESPONSE:", data)

    assert res.status_code == 200
    assert data["status"] == 200

    # check session
    with test_client.session_transaction() as sess:
        cart = sess.get(key, {})
        assert "1" in cart
        assert cart["1"]["quantity"] == 1