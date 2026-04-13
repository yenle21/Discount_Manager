import pytest
from flask import Flask
from datetime import datetime, timedelta

from discounts import db
from discounts.models import Voucher
from discounts.models import Product, Category   # thêm dòng này


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.secret_key = '^#@$*Juifdyfuhsfai#@&#^*'
    app.config['CART_KEY'] = 'cart'
    db.init_app(app)

    from discounts.index import register_routes
    register_routes(app)

    return app


# 🔹 App fixture
@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# 🔹 Client
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


# 🔹 DB session
@pytest.fixture
def test_session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_product(test_session):
    pass
    # p1 = Product(name= 'iPhone 17',price = 30 , category_id = 1)
    # p2 = Product(name= 'iPad Pro',price = 20 , category_id = 2)
    # p3 = Product(name= 'Galaxy S26 Ultra',price = 35 , category_id = 1)
    # p4 = Product(name= 'iPhone Ultra',price = 35 , category_id = 2)

    # test_session.add_all([p1,p2,p3, p4])
    # test_session.commit()
    #
    # yield [p1, p2, p3, p4]


@pytest.fixture
def sample_voucher(test_session):
    now = datetime.now()

    v1 = Voucher(
        MaGG = "MA1",
        Hinhthuc = "Khuyến mãi",
        LoaiGG = "phantram",
        GiaTri = 10.0,
        SoLuong = 100,
        NgayBD = now,
        NgayKT = now + timedelta(days=7),
        TrangThai = "active",
        MoTa = "Giảm 10% cho đơn hàng từ 200.000",
        DieuKien = 200000.0,
        DaSuDung = 0,
        DieuKienSP = "Sữa"
    )
    v2 = Voucher(
        MaGG = "MA2",
        Hinhthuc = "Shipping",
        LoaiGG = "tien",
        GiaTri = 10000.0,
        SoLuong = 10,
        NgayBD = now,
        NgayKT = now + timedelta(days=30),
        TrangThai = "active",
        MoTa = "Giảm 10.000 phí ship cho đơn hàng từ 100.000",
        DieuKien = 100000.0,
        DaSuDung = 5, # Đã có người dùng (để test không cho xóa)
        DieuKienSP = "Mì gói"
    )
    v3 = Voucher(
        MaGG = "MA3",
        Hinhthuc = "Khuyến mãi",
        LoaiGG = "phantram",
        GiaTri = 20.0,
        SoLuong = 500,
        NgayBD = now,
        NgayKT = now + timedelta(days=365),
        TrangThai = "inactive", #Chờ kích hoạt
        MoTa = "Giảm 20% cho đơn hàng từ 200.000",
        DieuKien = 200000.0,
        DaSuDung = 0,
        DieuKienSP = "Bột giặt"
    )
    v4 = Voucher(
        MaGG = "MA4",
        Hinhthuc = "Khuyến mãi",
        LoaiGG = "tien",
        GiaTri = 5000.0,
        SoLuong = 100,
        NgayBD = now - timedelta(days=10),
        NgayKT = now - timedelta(days=1),  # Đã hết hạn
        TrangThai = "inactive",
        MoTa = "Giảm 5.000 cho đơn hàng từ 50.000",
        DieuKien = 50000.0,
        DaSuDung = 100,
        DieuKienSP = "Kem"
    )

    vouchers = [v1, v2, v3, v4]
    test_session.add_all(vouchers)
    test_session.commit()

    return vouchers

@pytest.fixture()
def test_cloudinary(monkeypatch):
    def fake_upload(file):
        return{'secure_url':'https://fake-image.png'}

    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)
# 🔹 Sample data
# @pytest.fixture
# def sample_product(test_session):
#     cate1 = Category(id=1, name="Sữa")
#     cate2 = Category(id=2, name="Kem")
#
#     p1 = Product(id=1, name="Sữa Vinamilk", price=10, category_id=1)
#     p2 = Product(id=2, name="Sữa Nuti", price=12, category_id=1)
#     p3 = Product(id=3, name="Kem Bắp", price=8, category_id=2)
#
#     test_session.add_all([cate1, cate2, p1, p2, p3])
#     test_session.commit()
#
#     yield [p1, p2, p3]