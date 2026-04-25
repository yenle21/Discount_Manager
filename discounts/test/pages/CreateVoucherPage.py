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

    def createvoucher(self,magg,hinhthuc,loaigg,giatri,soluong,ngaybd,ngaykt,mota,dieukiensp,tientoithieu):
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
        self.driver.implicitly_wait(1)
        self.typing(*self.NGAYBD,ngaybd)
        self.driver.implicitly_wait(1)
        self.typing(*self.NGAYKT,ngaykt)
        self.driver.implicitly_wait(1)
        self.typing(*self.MOTA,mota)
        self.driver.implicitly_wait(1)
        self.select_dropdown(*self.DIEUKIENSP, dieukiensp)
        self.driver.implicitly_wait(1)
        self.typing(*self.DKTIENTOITHIEU, tientoithieu)
        self.driver.implicitly_wait(2)
        self.click(*self.BUTTON_SAVE)







