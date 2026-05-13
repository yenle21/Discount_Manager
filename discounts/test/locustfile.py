from locust import HttpUser, task, between, events
import gevent

class AdminUser(HttpUser):  # pragma: no cover
    """
    Mô phỏng hành vi của Admin:
      - Xem danh sách voucher
      - Tìm kiếm voucher theo từ khóa
      - Lọc voucher theo trạng thái
      - Lọc voucher theo hình thức
      - Mở trang tạo voucher
      - Tạo voucher mới
      - Mở trang sửa voucher
      - Sửa voucher
      - Xóa voucher
    """

    wait_time = between(1, 3)

    def on_start(self):
        self.client.post("/login", data={
            "role":     "1",
            "username": "admin",
            "password": "123",
        })

    @task(5)
    def xem_danh_sach_voucher(self):
        self.client.get("/admin", name="/admin")

    @task(4)
    def tim_kiem_theo_keyword(self):
        self.client.get("/admin?kw=SPRING", name="/admin?kw=")

    @task(3)
    def loc_theo_trang_thai_active(self):
        self.client.get("/admin?trang_thai=Active", name="/admin?trang_thai=Active")

    @task(2)
    def loc_theo_trang_thai_pending(self):
        self.client.get("/admin?trang_thai=pending", name="/admin?trang_thai=pending")

    @task(2)
    def loc_theo_trang_thai_expired(self):
        self.client.get("/admin?trang_thai=expired", name="/admin?trang_thai=expired")

    @task(2)
    def loc_theo_hinh_thuc_khuyenmai(self):
        self.client.get("/admin?hinh_thuc=Khuyến mãi", name="/admin?hinh_thuc=KhuyenMai")

    @task(2)
    def loc_theo_hinh_thuc_shipping(self):
        self.client.get("/admin?hinh_thuc=Shipping", name="/admin?hinh_thuc=Shipping")

    @task(2)
    def mo_trang_tao_voucher(self):
        self.client.get("/create", name="/create")

    @task(1)
    def tao_voucher(self):
        import random
        magg = f"PERF{random.randint(10000, 99999)}"
        self.client.post("/create", data={
            "MaGG":      magg,
            "Hinhthuc":  "Khuyến mãi",
            "LoaiGG":    "tien",
            "GiaTri":    "10000",
            "SoLuong":   "100",
            "NgayBD":    "2026-05-10T10:00",
            "NgayKT":    "2026-05-30T23:59",
            "MoTa":      "Voucher test hiệu năng",
            "DieuKienSP":"",
            "DieuKien":  "50000",
            "TrangThai": "active",
        }, name="/create [POST]")

    @task(2)
    def mo_trang_sua_voucher(self):
        self.client.get("/edit/SPRING26", name="/edit/<MaGG>")

    @task(1)
    def sua_voucher(self):
        self.client.post("/update/SPRING26", data={
            "Hinhthuc":  "Khuyến mãi",
            "LoaiGG":    "tien",
            "GiaTri":    "15000",
            "SoLuong":   "200",
            "NgayBD":    "2026-05-10T10:00",
            "NgayKT":    "2026-05-30T23:59",
            "MoTa":      "Cập nhật hiệu năng",
            "DieuKienSP":"",
            "DieuKien":  "50000",
            "TrangThai": "active",
        }, name="/update/<MaGG> [POST]")

class CustomerUser(HttpUser):
    """
    Mô phỏng hành vi của Khách hàng:
      - Xem trang chủ sản phẩm
      - Tìm kiếm sản phẩm
      - Lọc theo danh mục
      - Thêm vào giỏ hàng
      - Xem giỏ hàng
      - Áp dụng voucher
      - Xóa voucher
      - Thanh toán
    """

    wait_time = between(1, 5)

    def on_start(self):
        self.client.post("/login", data={
            "role":     "0",
            "username": "khachhang",
            "password": "123",
        })

    @task(5)
    def xem_trang_chu(self):
        self.client.get("/", name="/")

    @task(4)
    def tim_kiem_san_pham(self):
        self.client.get("/?kw=Sữa", name="/?kw=")

    @task(3)
    def loc_theo_danh_muc(self):
        self.client.get("/?category_id=1", name="/?category_id=")

    @task(3)
    def xem_trang_phan_trang(self):
        self.client.get("/?page=2", name="/?page=")

    @task(4)
    def them_vao_gio_hang(self):
        self.client.post("/api/cart", json={
            "id":          1,
            "name":        "Sữa TH",
            "price":       30000,
            "image":       "milk.jpg",
            "category_id": 1,
        }, name="/api/cart [POST]")

    @task(4)
    def xem_gio_hang(self):
        self.client.get("/cart", name="/cart")

    @task(2)
    def cap_nhat_so_luong(self):
        self.client.put("/api/cart/1", json={
            "quantity": 2,
        }, name="/api/cart/<id> [PUT]")

    @task(3)
    def xem_danh_sach_voucher(self):
        self.client.get("/voucher-list", name="/voucher-list")

    @task(3)
    def ap_dung_voucher(self):
        self.client.put("/api/apply-voucher/1", json={
            "voucher_id": "SPRING26",
        }, name="/api/apply-voucher [PUT]")

    @task(2)
    def xoa_voucher(self):
        self.client.delete("/api/apply-voucher", name="/api/apply-voucher [DELETE]")

    @task(1)
    def thanh_toan(self):
        self.client.post("/api/checkout", json={
            "receiver_name":    "Nguyễn Văn A",
            "receiver_phone":   "0321277291",
            "receiver_address": "Nhà Bè TPHCM",
            "payment_method":   "Tiền mặt",
        }, name="/api/checkout [POST]")

class GuestUser(HttpUser):
    """
    Mô phỏng hành vi của Khách chưa đăng nhập:
      - Xem trang chủ
      - Tìm kiếm sản phẩm
      - Thêm vào giỏ hàng
      - Xem giỏ hàng
    """

    wait_time = between(2, 6)

    @task(5)
    def xem_trang_chu(self):
        self.client.get("/", name="/")

    @task(3)
    def tim_kiem_san_pham(self):
        self.client.get("/?kw=Mì", name="/?kw=")

    @task(3)
    def them_vao_gio_hang(self):
        self.client.post("/api/cart", json={
            "id":          2,
            "name":        "Mì Hảo Hảo",
            "price":       20000,
            "image":       "mì.jpg",
            "category_id": 2,
        }, name="/api/cart [POST]")

    @task(2)
    def xem_gio_hang(self):
        self.client.get("/cart", name="/cart")

# Dừng sau 120 giây
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    def stop_after(seconds):
        gevent.sleep(seconds)
        environment.runner.quit()

    gevent.spawn(stop_after, 120)