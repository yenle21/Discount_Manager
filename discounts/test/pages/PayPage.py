import os
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from discounts.test.pages.BasePage import BasePage

class PayPage(BasePage):
    URL = "http://127.0.0.1:5000/cart"
    SCREENSHOT_DIR = "discounts/test/screenshots/Pay"

    # ── Locators – Thông tin nhận hàng ───────────────────────────────────
    INPUT_NAME    = (By.ID, "receiver-name")
    INPUT_PHONE   = (By.ID, "receiver-phone")
    INPUT_ADDRESS = (By.ID, "receiver-address")

    # ── Locators – Phương thức thanh toán ────────────────────────────────
    PAYMENT_SELECT = (By.ID, "payment-method")

    # ── Locators – Voucher ───────────────────────────────────────────────
    BTN_OPEN_VOUCHER   = (By.ID,          "apply-voucher-btn")
    BTN_CLEAR_VOUCHERS = (By.ID,          "btn-clear-vouchers")
    MODAL_BODY         = (By.CLASS_NAME,  "modal-body")
    VOUCHER_TABS       = (By.ID,          "voucherTab")

    # Tab pill buttons (trong modal)
    TAB_PROMO  = (By.ID, "promo-tab")
    TAB_SHIP   = (By.ID, "ship-tab")

    # Nút "Chọn" đầu tiên trong tab đang active
    BTN_CHON_FIRST = (By.CSS_SELECTOR,
                      ".tab-pane.active .btn.btn-primary.btn-sm")

    # Applied voucher badges (hiển thị trên trang cart sau khi chọn)
    APPLIED_BADGES = (By.CSS_SELECTOR, "#applied-vouchers-success .badge")

    # ── Locators – Giỏ hàng ──────────────────────────────────────────────
    CART_ITEMS     = (By.CSS_SELECTOR, "#cart-items-container > div.row")
    PRODUCT_NAMES  = (By.CLASS_NAME,  "product-name-text")
    QTY_INPUTS     = (By.CSS_SELECTOR, "input[type='number']")
    BTN_DELETE_FIRST = (By.CSS_SELECTOR,
                        "#cart-items-container .btn.btn-danger")

    # ── Locators – Tổng tiền ─────────────────────────────────────────────
    TOTAL_PRICE    = (By.CSS_SELECTOR, ".cart-price")
    TOTAL_NEWPRICE = (By.CSS_SELECTOR, ".cart-new-price")
    DISCOUNT_VAL   = (By.ID,          "discount-val")
    CART_COUNTER   = (By.ID,          "cart-counter")

    # ── Locators – Nút Thanh toán ─────────────────────────────────────────
    BTN_CHECKOUT   = (By.ID,          "btn-checkout-now")

    # ── Locators – Alert/Thông báo ───────────────────────────────────────
    ALERT_EL       = (By.CLASS_NAME,  "alert")
    LOGIN_LINK     = (By.LINK_TEXT,   "Đăng nhập")

    # ── Navigation ────────────────────────────────────────────────────────

    def open_page(self):
        """Mở trang /cart."""
        self.open(self.URL)

    def screenshot(self, name: str):
        os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        self.driver.save_screenshot(f"{self.SCREENSHOT_DIR}/{name}.png")
    # ── Thông tin nhận hàng ───────────────────────────────────────────────

    def enter_info(self, name: str, phone: str, address: str):
        """
        Điền đầy đủ thông tin người nhận hàng.
        Truyền chuỗi rỗng "" để kiểm tra validate.
        """
        name_el = self.find(*self.INPUT_NAME)
        name_el.clear()
        name_el.send_keys(name)

        phone_el = self.find(*self.INPUT_PHONE)
        phone_el.clear()
        phone_el.send_keys(phone)

        addr_el = self.find(*self.INPUT_ADDRESS)
        addr_el.clear()
        addr_el.send_keys(address)

    def get_name(self) -> str:
        return self.find(*self.INPUT_NAME).get_attribute("value")

    def get_phone(self) -> str:
        return self.find(*self.INPUT_PHONE).get_attribute("value")

    def get_address(self) -> str:
        return self.find(*self.INPUT_ADDRESS).get_attribute("value")

    # ── Phương thức thanh toán ────────────────────────────────────────────

    def get_payment(self):
        """Trả về element Select phương thức thanh toán (để test options)."""
        return self.find(*self.PAYMENT_SELECT)

    def select_payment(self, method: str):
        """
        Chọn phương thức thanh toán.
        method: "COD" hoặc "Chuyển khoản"
        """
        sel = Select(self.find(*self.PAYMENT_SELECT))
        options = sel.options
        for opt in options:
            if method.lower() in opt.text.lower():
                opt.click()
                return
        # fallback: chọn theo index
        if method == "COD":
            sel.select_by_index(0)
        else:
            sel.select_by_index(1)

    def get_payment_options(self) -> list[str]:
        """Lấy danh sách text của tất cả option trong dropdown thanh toán."""
        sel = Select(self.find(*self.PAYMENT_SELECT))
        return [o.text for o in sel.options]

    # ── Voucher ───────────────────────────────────────────────────────────

    def open_voucher(self):
        """Click nút 'Sử dụng Mã giảm giá' để mở modal."""
        self.click(*self.BTN_OPEN_VOUCHER)
        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(self.MODAL_BODY)
        )

    def select_voucher_tab(self, tab_name: str):
        """
        Chọn tab trong modal voucher.
        tab_name: "Khuyến mãi" | "Miễn phí ship"
        """
        if "ship" in tab_name.lower() or "vận" in tab_name.lower():
            self.click(*self.TAB_SHIP)
        else:
            self.click(*self.TAB_PROMO)
        time.sleep(0.5)

    def choose_voucher(self):
        """Click nút 'Chọn' đầu tiên trong tab đang active."""
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(self.BTN_CHON_FIRST)
        )
        self.click(*self.BTN_CHON_FIRST)
        time.sleep(1)

    def select_voucher_by_code(self, magg: str):
        """
        Tìm và click nút 'Chọn' của voucher có mã magg trong modal.
        Raise NoSuchElementException nếu không tìm thấy.
        """
        cards = self.driver.find_elements(
            By.CSS_SELECTOR, ".tab-pane.active .card"
        )
        for card in cards:
            if magg.upper() in card.text.upper():
                btn = card.find_element(By.CSS_SELECTOR, "button.btn-primary")
                btn.click()
                time.sleep(1)
                return
        raise NoSuchElementException(f"Không tìm thấy voucher '{magg}' trong modal")

    def remove_voucher(self):
        """Click nút 'Xóa tất cả' voucher đã áp dụng."""
        self.click(*self.BTN_CLEAR_VOUCHERS)
        time.sleep(1)

    def get_applied_vouchers(self) -> list[str]:
        """Lấy danh sách text của các badge voucher đã được áp dụng."""
        badges = self.driver.find_elements(*self.APPLIED_BADGES)
        return [b.text.strip() for b in badges]

    # ── Giỏ hàng ─────────────────────────────────────────────────────────

    def get_cart_items(self):
        """Lấy các dòng sản phẩm trong giỏ hàng."""
        return self.driver.find_elements(*self.CART_ITEMS)

    def delete_item(self):
        """Click nút 'Xóa' của sản phẩm đầu tiên trong giỏ."""
        self.click(*self.BTN_DELETE_FIRST)
        time.sleep(1)

    def update_quantity(self, qty: int):
        """Cập nhật số lượng của sản phẩm đầu tiên."""
        inputs = self.driver.find_elements(*self.QTY_INPUTS)
        if inputs:
            el = inputs[0]
            el.clear()
            el.send_keys(str(qty))
            el.send_keys("\t")   # blur để trigger updateCart()
            time.sleep(1)

    def get_quantity(self) -> str:
        """Lấy giá trị số lượng của sản phẩm đầu tiên."""
        inputs = self.driver.find_elements(*self.QTY_INPUTS)
        if inputs:
            return inputs[0].get_attribute("value")
        return "0"

    # ── Tổng tiền ─────────────────────────────────────────────────────────

    def get_total(self) -> str:
        """Lấy text tổng tiền ban đầu (trước giảm giá)."""
        return self.find(*self.TOTAL_PRICE).text

    def get_total_new(self) -> str:
        """Lấy text tổng tiền phải thanh toán (sau giảm giá)."""
        return self.find(*self.TOTAL_NEWPRICE).text

    def get_discount_amount(self) -> str:
        """Lấy text số tiền giảm (ví dụ '-10,000đ')."""
        return self.find(*self.DISCOUNT_VAL).text

    def get_cart_counter(self) -> str:
        """Lấy số sản phẩm trong giỏ hàng từ badge counter."""
        return self.find(*self.CART_COUNTER).text.strip()

    # ── Thanh toán ────────────────────────────────────────────────────────

    def checkout(self):
        """
        Click nút 'Thanh toán ngay'.
        Tự động accept alert/confirm nếu xuất hiện.
        """
        self.click(*self.BTN_CHECKOUT)
        time.sleep(1)
        try:
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert.accept()
            time.sleep(1)
        except TimeoutException:
            pass

    def checkout_and_cancel(self):
        """
        Click nút 'Thanh toán ngay' rồi DISMISS (Cancel) popup xác nhận.
        Dùng để test TC_CK_14.
        """
        self.click(*self.BTN_CHECKOUT)
        time.sleep(1)
        try:
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert.dismiss()
            time.sleep(1)
        except TimeoutException:
            pass

    def is_checkout_btn_visible(self) -> bool:
        """Trả True nếu nút Thanh toán ngay tồn tại và hiển thị."""
        try:
            btn = self.driver.find_element(*self.BTN_CHECKOUT)
            return btn.is_displayed()
        except NoSuchElementException:
            return False

    def is_login_link_visible(self) -> bool:
        """Trả True nếu link 'Đăng nhập' được hiển thị (chưa login)."""
        try:
            link = self.driver.find_element(*self.LOGIN_LINK)
            return link.is_displayed()
        except NoSuchElementException:
            return False

    # ── Lấy thông báo / alert ─────────────────────────────────────────────

    def get_all_alerts(self) -> list[str]:
        """
        Thu thập tất cả thông báo:
        - Browser alert / confirm
        - DOM .alert
        - SweetAlert2 popup
        Trả về list[str], tự động accept alert.
        """
        msgs = []

        # 1. Browser alert
        try:
            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            msgs.append(alert.text)
            alert.accept()
            time.sleep(0.5)
        except TimeoutException:
            pass

        # 2. DOM alert / SweetAlert
        for sel in [
            ".alert",
            ".swal2-popup",
            ".swal2-html-container",
            "[role='alert']",
        ]:
            try:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                msgs += [e.text for e in els if e.text.strip()]
            except Exception:
                pass

        return msgs

    def wait_for_redirect(self, expected_url_contains: str, timeout: int = 10):
        """Chờ trang redirect đến URL chứa chuỗi expected_url_contains."""
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(expected_url_contains)
        )