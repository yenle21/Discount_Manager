import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By

from discounts.test.pages.ApplyVoucherPage import  ApplyVoucherPage
from discounts.test.conftest import driver, cart_ready


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

def test_TC05_show_voucher(cart_ready):
    driver = cart_ready
    cart = ApplyVoucherPage(driver)
    cart.open_page()

    cart.open_voucher()

    vouchers = cart_ready.find_elements(By.CLASS_NAME, "card-body")

    assert len(vouchers) > 0
    driver.save_screenshot("discounts/test/screenshots/ApplyVoucher/actual_output_TC05.png")

# def test_TC06_remove_voucher(cart_ready):
#     cart = ApplyVoucherPage(cart_ready)
#     cart.open_page()
#     cart.choose_voucher()
#
#     before = cart.get_total_new()
#
#     cart.remove_voucher()
#
#     after = cart.get_total_new()
#
#     assert before != after