from selenium.common.exceptions import NoSuchElementException

from discounts.test.pages.CartPage import CartPage
from discounts.test.pages.HomePage import HomePage
from discounts.test.pages.LoginPage import LoginPage
from discounts.test.conftest import driver
from selenium.webdriver.common.by import By
import time
import pytest


def test_search_products(driver):
    home = HomePage(driver=driver)

    kw = 'iPad'
    home.open_page()
    home.search(kw)

    time.sleep(1)

    results = driver.find_elements(By.CSS_SELECTOR, '.container .card-title')
    assert all(kw in r.text for r in results)

def test_login_success(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('admin', '123456')

    time.sleep(2)

    assert driver.current_url == 'http://127.0.0.1:5000/'

    e = driver.find_element(By.CSS_SELECTOR, '#collapsibleNavbar > ul > li:nth-child(5) > a')
    assert 'admin' in e.text

def test_login_from_cart(driver):
    login = LoginPage(driver)
    login.open_page(url='http://127.0.0.1:5000/login?next=/cart')
    login.login('admin', '123456')

    time.sleep(2)

    assert driver.current_url == 'http://127.0.0.1:5000/cart'

    e = driver.find_element(By.CSS_SELECTOR, '#collapsibleNavbar > ul > li:nth-child(5) > a')
    assert 'admin' in e.text

def test_add_to_cart(driver):
    home = HomePage(driver=driver)
    home.open_page()
    home.add_to_cart()

    e = driver.find_element(By.CLASS_NAME, 'cart-counter')
    assert int(e.text) == 3

def test_receipt(driver):
    home = HomePage(driver=driver)
    home.open_page()
    home.add_to_cart()

    login = LoginPage(driver=driver)
    login.open_page()
    login.login('admin', '123456')

    time.sleep(2)

    p = CartPage(driver=driver)
    p.open_page()
    p.add_receipt()

    time.sleep(1)
    with pytest.raises(NoSuchElementException):
        driver.find_element(By.TAG_NAME, 'table')