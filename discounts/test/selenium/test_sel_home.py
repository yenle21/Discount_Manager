from selenium.webdriver.common.by import By

from discounts.test.pages.HomePage import HomePage
from discounts.test.pages.LoginPage import LoginPage
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def test_TC01_click_logo_redirect_home(driver):
    driver.get("http://127.0.0.1:5000/cart")

    home = HomePage(driver)
    home.click_logo()

    assert driver.current_url == 'http://127.0.0.1:5000/'


def test_TC02_click_login_redirect(driver):
    home = HomePage(driver)
    home.open_page()
    home.click_login()

    assert driver.current_url == 'http://127.0.0.1:5000/login'


def test_TC03_click_register_redirect(driver):
    home = HomePage(driver)
    home.open_page()
    home.click_register()

    assert driver.current_url == 'http://127.0.0.1:5000/register'

def test_TC04_header_after_login(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    home = HomePage(driver)

    # wait sau login
    home.wait.until(lambda d: home.is_logout_visible())

    # ❌ login/register không còn
    assert not home.is_login_visible()
    assert not home.is_register_visible()

    # ✔ hiển thị logout + username
    assert home.is_logout_visible()
    assert home.get_username() != ""

    # ✔ có quản lý voucher
    assert home.is_voucher_visible()
    driver.save_screenshot("discounts/test/screenshots/Home/actual_output_TC04.png")

def test_TC05_click_username_no_redirect(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")


    home = HomePage(driver)
    current_url = driver.current_url

    driver.find_element(*home.USER_NAME).click()

    assert driver.current_url == current_url

def test_TC06_logout(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login("Khách Hàng", "khachhang", "123")

    home = HomePage(driver)

    home.wait.until(lambda d: home.is_logout_visible())
    home.click_logout()

    # 🔥 đợi voucher biến mất
    home.wait.until_not(
        EC.visibility_of_element_located(home.VOUCHER_MANAGER)
    )

    # ✔ trạng thái sau logout
    assert home.is_login_visible()
    assert home.is_register_visible()

    # ❌ không còn
    assert not home.is_logout_visible()
    assert not home.is_voucher_visible()
    driver.save_screenshot("discounts/test/screenshots/Home/actual_output_TC06.png")

def test_TC07_display_categories(driver):
    home = HomePage(driver)
    home.open_page()

    home.open_category_dropdown()
    driver.save_screenshot("discounts/test/screenshots/Home/actual_output_TC07.png")

    categories = [c.text for c in home.get_all_categories()]

    assert "Sữa" in categories
    assert "Mì Gói" in categories
    assert "Bột Giặt" in categories
    assert "Kem" in categories


def test_TC08_filter_by_category(driver):
    home = HomePage(driver)
    home.open_page()

    home.open_category_dropdown()
    home.select_category("Sữa")

    # wait load lại sản phẩm
    WebDriverWait(driver, 10).until(
        lambda d: len(home.get_product_names()) > 0
    )

    products = home.get_product_names()
    driver.save_screenshot("discounts/test/screenshots/Home/actual_output_TC08.png")

    # ✔ tất cả sản phẩm phải chứa "Sữa"
    for p in products:
        assert "Sữa" in p

def test_TC09_search_exact_product(driver):
    home = HomePage(driver)
    home.open_page()

    home.search("Sữa Vinamilk")

    # wait kết quả
    home.wait.until(lambda d: len(home.get_product_names()) > 0)

    products = home.get_product_names()
    driver.save_screenshot("discounts/test/screenshots/Home/actual_output_TC09.png")

    # ✔ phải có sản phẩm đúng
    assert any("Sữa Vinamilk" in p for p in products)

def test_TC10_search_not_found(driver):
    home = HomePage(driver)
    home.open_page()

    home.search("jhfgfiy")

    # wait message xuất hiện
    msg = driver.find_element(By.CLASS_NAME, "text-muted")

    assert "Không có sản phẩm" in msg.text

    # ✔ nút quay lại tồn tại
    assert home.is_element_visible(home.BACK_HOME_BTN)
    driver.save_screenshot("discounts/test/screenshots/Home/actual_output_TC10.png")

def test_TC11_back_to_home(driver):
    home = HomePage(driver)
    home.open_page()

    home.search("jhfgfiy")

    # wait empty state
    home.wait.until(lambda d: home.is_element_visible(home.BACK_HOME_BTN))

    home.click_back_home()

    # wait về homepage
    home.wait.until(lambda d: d.current_url.endswith("/"))

    assert driver.current_url.endswith("/")

def test_TC12_pagination(driver):
    home = HomePage(driver)
    home.open_page()

    home.click_page(2)

    # wait đến khi active page = 2
    WebDriverWait(driver, 10).until(
        lambda d: home.get_active_page() == "2"
    )

    assert home.get_active_page() == "2"

def test_add_to_cart_success(test_client, app):
    key = app.config['CART_KEY']

    res = test_client.post("/api/cart", json={
        "id": 1,
        "name": "Sữa tươi",
        "price": 50000,
        "image": "milk.jpg",
        "category_id": 1
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