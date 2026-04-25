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

    def createvoucher(self,magg,hinhthuc,loaigg,giatri,soluong,mota,dieukiensp,tientoithieu):
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
        ngaybd_input = self.find(*self.NGAYBD)
        self.driver.implicitly_wait(1)
        ngaybd_input.click()  # Bắt buộc phải click vào để nháy con trỏ ở tháng (mm)
        self.driver.implicitly_wait(1)
        ngaybd_input.send_keys("05012026")
        # Bấm nút TAB hoặc Mũi tên phải trên bàn phím để nhảy qua phần điền Giờ
        ngaybd_input.send_keys(Keys.RIGHT)
        self.driver.implicitly_wait(1)
        ngaybd_input.send_keys("1000A")
        ngaykt_input = self.find(*self.NGAYKT)
        ngaykt_input.click()
        ngaykt_input.send_keys("05302026")
        ngaykt_input.send_keys(Keys.RIGHT)
        ngaykt_input.send_keys("1159P")
        self.driver.implicitly_wait(1)
        self.typing(*self.MOTA,mota)
        self.driver.implicitly_wait(1)
        self.select_dropdown(*self.DIEUKIENSP, dieukiensp)
        self.driver.implicitly_wait(1)
        self.typing(*self.DKTIENTOITHIEU, tientoithieu)
        self.driver.implicitly_wait(2)
        self.click(*self.BUTTON_SAVE)







