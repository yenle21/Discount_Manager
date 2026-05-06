import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from discounts.test.pages.BasePage import BasePage

class CreateVoucherPage2(BasePage):
    URL = "http://127.0.0.1:5000/create"
    ADMIN_URL = "http://127.0.0.1:5000/admin"
    SCREENSHOT_DIR = "discounts/test/screenshots/CreateVoucher2"

    MAGG           = (By.NAME, "MaGG")
    HINHTHUC       = (By.NAME, "Hinhthuc")
    LOAIGG         = (By.NAME, "LoaiGG")
    GIATRI         = (By.NAME, "GiaTri")
    SOLUONG        = (By.NAME, "SoLuong")
    NGAYBD         = (By.NAME, "NgayBD")
    NGAYKT         = (By.NAME, "NgayKT")
    MOTA           = (By.NAME, "MoTa")
    DIEUKIENSP     = (By.NAME, "DieuKienSP")
    DKTIENTOITHIEU = (By.NAME, "DieuKien")

    RADIO_ACTIVE   = (By.CSS_SELECTOR, "input[name='TrangThai'][value='active']")
    RADIO_INACTIVE = (By.CSS_SELECTOR, "input[name='TrangThai'][value='inactive']")

    BUTTON_SAVE   = (By.CSS_SELECTOR, "button.btn-submit")
    BUTTON_CANCEL = (By.CSS_SELECTOR, "button.btn-cancel")

    ALERT      = (By.CLASS_NAME, "alert")
    TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")

    STATUS_BADGE   = (By.CSS_SELECTOR, ".status-badge")
    HINHTHUC_BADGE = (By.CSS_SELECTOR, ".badge")

    def open_page(self):
        self.open(self.URL)

    def open_admin(self):
        self.open(self.ADMIN_URL)

    def screenshot(self, name: str):
        os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
        self.driver.save_screenshot(f"{self.SCREENSHOT_DIR}/{name}.png")

    def createvoucher(
        self,
        magg:          str = None,
        hinhthuc:      str = None,
        loaigg:        str = None,
        giatri:        str = None,
        soluong:       str = None,
        ngaybd_date:   str = None,
        ngaybd_time:   str = None,
        ngaykt_date:   str = None,
        ngaykt_time:   str = None,
        mota:          str = None,
        dieukiensp:    str = None,
        tientoithieu:  str = None,
        trangthai:     str = None,
    ):
        self.driver.implicitly_wait(1)

        if magg is not None:
            self.typing(*self.MAGG, magg)
            self.driver.implicitly_wait(1)

        if hinhthuc is not None:
            self.select_dropdown(*self.HINHTHUC, hinhthuc)
            self.driver.implicitly_wait(1)

        if loaigg is not None:
            self.select_dropdown(*self.LOAIGG, loaigg)
            self.driver.implicitly_wait(1)

        if trangthai == "active":
            self.driver.execute_script("window.scrollTo(0, 500)")
            self.click(*self.RADIO_ACTIVE)
        elif trangthai == "inactive":
            self.driver.execute_script("window.scrollTo(0, 500)")
            self.click(*self.RADIO_INACTIVE)

        if soluong is not None:
            self.typing(*self.SOLUONG, soluong)
            self.driver.implicitly_wait(1)

        if ngaybd_date is not None:
            ngaybd_input = self.find(*self.NGAYBD)

            day   = ngaybd_date[:2]
            month = ngaybd_date[2:4]
            year  = ngaybd_date[4:]

            hour_val = int(ngaybd_time[:2])
            if "P" in ngaybd_time.upper() and hour_val < 12:
                hour_val += 12
            elif "A" in ngaybd_time.upper() and hour_val == 12:
                hour_val = 0

            hour   = str(hour_val).zfill(2)
            minute = ngaybd_time[2:4]

            iso_value = f"{year}-{month}-{day}T{hour}:{minute}"

            self.driver.execute_script(
                "arguments[0].value = arguments[1]", ngaybd_input, iso_value
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'))", ngaybd_input
            )

        if ngaykt_date is not None:
            ngaykt_input = self.find(*self.NGAYKT)

            day   = ngaykt_date[:2]
            month = ngaykt_date[2:4]
            year  = ngaykt_date[4:]

            hour_val = int(ngaykt_time[:2])
            if "P" in ngaykt_time.upper() and hour_val < 12:
                hour_val += 12
            elif "A" in ngaykt_time.upper() and hour_val == 12:
                hour_val = 0

            hour   = str(hour_val).zfill(2)
            minute = ngaykt_time[2:4]

            iso_value = f"{year}-{month}-{day}T{hour}:{minute}"

            self.driver.execute_script(
                "arguments[0].value = arguments[1]", ngaykt_input, iso_value
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'))", ngaykt_input
            )

        if giatri is not None:
            self.typing(*self.GIATRI, giatri)
            self.driver.implicitly_wait(1)

        if mota is not None:
            self.typing(*self.MOTA, mota)
            self.driver.implicitly_wait(1)

        if dieukiensp is not None:
            self.select_dropdown(*self.DIEUKIENSP, dieukiensp)
            self.driver.implicitly_wait(1)

        if tientoithieu is not None:
            self.typing(*self.DKTIENTOITHIEU, tientoithieu)
            self.driver.implicitly_wait(1)

    def click_save(self):
        self.click(*self.BUTTON_SAVE)
        time.sleep(1)

    def click_cancel(self):
        self.click(*self.BUTTON_CANCEL)
        time.sleep(1)

    def get_alert_text(self) -> str:
        return self.find(*self.ALERT).text

    def get_giatri_value(self) -> str:
        return self.find(*self.GIATRI).get_attribute("value")

    def get_magg_value(self) -> str:
        return self.find(*self.MAGG).get_attribute("value")

    def get_soluong_value(self) -> str:
        return self.find(*self.SOLUONG).get_attribute("value")

    def get_table_rows(self):
        return self.driver.find_elements(*self.TABLE_ROWS)

    def get_row_by_magg(self, magg: str):
        for row in self.get_table_rows():
            if magg in row.text:
                return row
        return None

    def get_status_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            badge = row.find_element(*self.STATUS_BADGE)
            return badge.text.strip().lower()
        return ""

    def get_hinhthuc_badge_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            badge = row.find_element(*self.HINHTHUC_BADGE)
            return badge.text.strip()
        return ""

    def get_soluong_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            usage = row.find_element(By.CSS_SELECTOR, ".usage-text")
            return usage.text.strip()
        return ""

    def get_ngaybd_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            cells = row.find_elements(By.TAG_NAME, "td")
            return cells[5].get_attribute("innerText").strip()
        return ""

    def get_ngaykt_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            cells = row.find_elements(By.TAG_NAME, "td")
            return cells[6].get_attribute("innerText").strip()
        return ""

    def get_mota_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            desc = row.find_element(By.CSS_SELECTOR, ".voucher-desc")
            return desc.text.strip()
        return ""

    def get_dieukien_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            cells = row.find_elements(By.TAG_NAME, "td")
            return cells[7].text.strip()
        return ""

    def get_dieukiensp_in_row(self, magg: str) -> str:
        row = self.get_row_by_magg(magg)
        if row:
            cells = row.find_elements(By.TAG_NAME, "td")
            return cells[8].text.strip()
        return ""

    def get_magg_validation_message(self) -> str:
        return self.find(*self.MAGG).get_attribute("validationMessage")

    def get_soluong_validation_message(self) -> str:
        return self.find(*self.SOLUONG).get_attribute("validationMessage")

    def get_ngaybd_validation_message(self) -> str:
        return self.find(*self.NGAYBD).get_attribute("validationMessage")

    def get_ngaykt_validation_message(self) -> str:
        return self.find(*self.NGAYKT).get_attribute("validationMessage")