from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash
import json
import os
from discounts import db

class UserRole:
    ADMIN = 1
    KHACHHANG = 0

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Integer, default=0)
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(100))
    sdt = db.Column(db.String(20))
    type = db.Column(db.String(20))
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': 'user'}

class KhachHang(User):
    # Dùng chuỗi 'DonHang' để tránh lỗi Multiple classes found
    don_hangs = db.relationship('DonHang', backref='khach_hang_ref', lazy=True)
    __mapper_args__ = {'polymorphic_identity': 'khachhang'}

class Admin(User):
    ma_giam_gias = db.relationship('Voucher', backref='admin_created_ref', lazy=True)
    __mapper_args__ = {'polymorphic_identity': 'admin'}

class Category(db.Model):
    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category_ref', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    LoaiSP = db.Column(db.String(50))
    image = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    chi_tiet_don_hang = db.relationship('CTHD', backref='san_pham_ref', lazy=True)

class Voucher(db.Model):
    __tablename__ = 'voucher'
    __table_args__ = {'extend_existing': True}
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
    don_hangs = db.relationship('DonHang', backref='voucher_applied_ref', lazy=True)

class DonHang(db.Model):
    __tablename__ = 'don_hang'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    HinhThucTT = db.Column(db.String(50))
    NgayLapDon = db.Column(db.DateTime, default=datetime.utcnow)
    TrangThai = db.Column(db.String(50), default="Pending")
    khach_hang_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ma_giam_gia_id = db.Column(db.String(50), db.ForeignKey('voucher.MaGG'))
    chi_tiet = db.relationship('CTHD', backref='don_hang_parent_ref', lazy=True)

class CTHD(db.Model):
    __tablename__ = 'cthd'
    __table_args__ = {'extend_existing': True}
    MaSP = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    MaHD = db.Column(db.Integer, db.ForeignKey('don_hang.id'), primary_key=True)
    TongTien = db.Column(db.Float)
    SoLuong = db.Column(db.Integer)
    TenNguoiNhan = db.Column(db.String(100))
    SDT = db.Column(db.String(20))
    DiaChi = db.Column(db.String(255))

from discounts import app
if __name__ == "__main__":
    with app.app_context():
        # Tạo bảng nếu chưa có
        db.create_all()

        # --- 1. TẠO ADMIN & KHÁCH HÀNG ---
        # Lưu ý: Admin id thường sẽ là 1 nếu tạo đầu tiên
        if not db.session.query(Admin).filter_by(username="admin").first():
            admin_user = Admin(
                name="Admin",
                username="admin",
                password=generate_password_hash("123"),
                user_role=UserRole.ADMIN
            )
            db.session.add(admin_user)

        if not db.session.query(KhachHang).filter_by(username="khachhang").first():
            db.session.add(KhachHang(
                name="Nguyễn Văn Khách",
                username="khachhang",
                password=generate_password_hash("123"),
                user_role=UserRole.KHACHHANG,
                email="kh@example.com",
                sdt="0901234567"
            ))

        db.session.commit()

        # --- 2. TẠO CATEGORY & PRODUCT (Từ file JSON) ---
        if os.path.exists("data/category.json"):
            with open("data/category.json", encoding="utf-8") as f:
                categories = json.load(f)
                for c in categories:
                    if not db.session.get(Category, c['id']):
                        db.session.add(Category(**c))
            db.session.commit()

        if os.path.exists("data/product.json"):
            with open("data/product.json", encoding="utf-8") as f:
                products = json.load(f)
                for p in products:
                    if not db.session.get(Product, p['id']):
                        db.session.add(Product(**p))
            db.session.commit()


        db.session.commit()
        print("---Database update thành công! ---")