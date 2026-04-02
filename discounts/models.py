from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash
import json
import os

# Giả sử db và app được import từ file khởi tạo chính
from discounts import db, app


class UserRole:
    ADMIN = 1
    KHACHHANG = 0


# --- MODELS ---

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Integer, default=0)

    type = db.Column(db.String(20))
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'user'
    }


class KhachHang(User):
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(100))
    sdt = db.Column(db.String(20))
    don_hangs = db.relationship('DonHang', backref='khach_hang', lazy=True)

    __mapper_args__ = {'polymorphic_identity': 'khachhang'}


class Admin(User):
    ma_giam_gias = db.relationship('Voucher', backref='admin_created', lazy=True)

    __mapper_args__ = {'polymorphic_identity': 'admin'}


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category_ref', lazy=True)


class Product(db.Model):
    __tablename__ = 'product'  # Sửa từ san_pham để đồng bộ với ForeignKey bên dưới
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    LoaiSP = db.Column(db.String(50))
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    chi_tiet_don_hang = db.relationship('CTHD', backref='san_pham', lazy=True)


class Voucher(db.Model):
    __tablename__ = 'voucher'
    MaGG = db.Column(db.String(50), primary_key=True)
    Hinhthuc = db.Column(db.String(50))
    LoaiGG = db.Column(db.String(50))
    GiaTri = db.Column(db.Float)
    SoLuong = db.Column(db.Integer)
    NgayBD = db.Column(db.DateTime, default=datetime.utcnow)
    NgayKT = db.Column(db.DateTime)
    TrangThai = db.Column(db.String(20))
    MoTa = db.Column(db.Text)
    DieuKien = db.Column(db.Float)
    DaSuDung = db.Column(db.Integer, default=0)
    DieuKienSP = db.Column(db.String(100))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    don_hangs = db.relationship('DonHang', backref='voucher_ref', lazy=True)


class DonHang(db.Model):
    __tablename__ = 'don_hang'
    id = db.Column(db.Integer, primary_key=True)
    HinhThucTT = db.Column(db.String(50))
    NgayLapDon = db.Column(db.DateTime, default=datetime.utcnow)
    TrangThai = db.Column(db.String(50), default="Pending")
    khach_hang_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ma_giam_gia_id = db.Column(db.String(50), db.ForeignKey('voucher.MaGG'))
    chi_tiet = db.relationship('CTHD', backref='don_hang', lazy=True)


class CTHD(db.Model):
    __tablename__ = 'cthd'
    MaSP = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    MaHD = db.Column(db.Integer, db.ForeignKey('don_hang.id'), primary_key=True)
    TongTien = db.Column(db.Float)
    SoLuong = db.Column(db.Integer)
    TenNguoiNhan = db.Column(db.String(100))
    SDT = db.Column(db.String(20))
    DiaChi = db.Column(db.String(255))


# --- PHẦN KHỞI TẠO DỮ LIỆU ---

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # 1. Tạo Admin & Khách hàng
        if not Admin.query.filter_by(username="admin").first():
            db.session.add(Admin(name="Admin System", username="admin",
                                 password=generate_password_hash("123"), user_role=UserRole.ADMIN))

        if not KhachHang.query.filter_by(username="khachhang").first():
            db.session.add(KhachHang(name="Nguyễn Văn B", username="khachhang",
                                     password=generate_password_hash("123"),
                                     user_role=UserRole.KHACHHANG, email="kh@example.com", sdt="0901234567"))

        db.session.commit()

        # 2. Tạo Category (Phải tạo trước Product vì Product cần category_id)
        # 2. Tạo Category
        if os.path.exists("data/category.json"):
            with open("data/category.json", encoding="utf-8") as f:
                categories = json.load(f)
                for c in categories:
                    # Thay đổi ở đây: dùng db.session.get
                    if not db.session.get(Category, c['id']):
                        db.session.add(Category(**c))
            db.session.commit()

        # 3. Tạo Sản phẩm
        if os.path.exists("data/product.json"):
            with open("data/product.json", encoding="utf-8") as f:
                products = json.load(f)
                for p in products:
                    # Thay đổi ở đây: dùng db.session.get
                    if not db.session.get(Product, p['id']):
                        db.session.add(Product(**p))
            db.session.commit()

        # 4. Tạo Mã giảm giá mẫu
        # Thay đổi ở đây: dùng db.session.get
        if not db.session.get(Voucher, "GIAM10K"):
            m1 = Voucher(
                MaGG="GIAM10K",
                Hinhthuc="Tiền mặt",
                LoaiGG="Giảm đơn",
                GiaTri=10000,
                SoLuong=100,
                NgayBD=datetime.now(),
                NgayKT=datetime(2026, 12, 31),
                TrangThai="Active",
                MoTa="Giảm 10k",
                admin_id=1
            )
            db.session.add(m1)

        db.session.commit()
        print("--- Đã khởi tạo dữ liệu thành công! ---")