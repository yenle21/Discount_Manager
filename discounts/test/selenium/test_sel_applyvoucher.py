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