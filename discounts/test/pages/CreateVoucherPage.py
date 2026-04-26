import time

from selenium.webdriver import Keys

from discounts.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class CreateVoucherPage(BasePage):
    URL = 'http://127.0.0.1:5000/create'
    MAGG= (By.NAME, 'MaGG')
    HINHTHUC= (By.NAME, 'Hinhthuc')
    LOAIGG=(By.ID, 'loaiGG')
    GIATRI=(By.NAME, 'GiaTri')
    SOLUONG= (By.NAME, 'SoLuong')
    NGAYBD = (By.NAME, 'NgayBD')
    NGAYKT = (By.NAME, 'NgayKT')
    MOTA = (By.NAME, 'MoTa')
    DIEUKIENSP = (By.NAME, 'DieuKienSP')
    DKTIENTOITHIEU = (By.NAME, 'DieuKien')
    TRANGTHAI = (By.NAME, 'TrangThai')
    BUTTON_SAVE = (By.CLASS_NAME, 'btn-submit')

    def open_page(self):
        self.open(self.URL)

    def createvoucher(self,magg,hinhthuc,loaigg,giatri,soluong,ngaybd_date, ngaybd_time, ngaykt_date, ngaykt_time,mota,dieukiensp,tientoithieu):
        self.driver.implicitly_wait(1)
        self.typing(*self.MAGG,magg)
        self.driver.implicitly_wait(1)
        self.select_dropdown(*self.HINHTHUC,hinhthuc)
        self.driver.implicitly_wait(1)
        self.select_dropdown(*self.LOAIGG,loaigg)
        self.driver.implicitly_wait(1)
        self.typing(*self.GIATRI,giatri)
        self.driver.implicitly_wait(1)
        self.typing(*self.SOLUONG,soluong)
        self.driver.execute_script('window.scrollTo(0,1000)')
        time.sleep(1)
        # --- ĐIỀN NGÀY BẮT ĐẦU (Nhận từ biến truyền vào) ---
        ngaybd_input = self.find(*self.NGAYBD)
        ngaybd_input.click()
        ngaybd_input.send_keys(ngaybd_date)
        ngaybd_input.send_keys(Keys.RIGHT)
        ngaybd_input.send_keys(ngaybd_time)

        # --- ĐIỀN NGÀY KẾT THÚC (Nhận từ biến truyền vào) ---
        ngaykt_input = self.find(*self.NGAYKT)
        ngaykt_input.click()
        ngaykt_input.send_keys(ngaykt_date)
        ngaykt_input.send_keys(Keys.RIGHT)
        ngaykt_input.send_keys(ngaykt_time)
        self.driver.implicitly_wait(1)
        self.typing(*self.MOTA,mota)
        self.driver.implicitly_wait(1)
        self.select_dropdown(*self.DIEUKIENSP, dieukiensp)
        self.driver.implicitly_wait(1)
        self.typing(*self.DKTIENTOITHIEU, tientoithieu)

    def click_save(self):
        self.click(*self.BUTTON_SAVE)







