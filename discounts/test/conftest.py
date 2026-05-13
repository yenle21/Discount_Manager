import datetime
import os
import time

import pytest
from flask import Flask
from discounts import db, login

from discounts.models import Product, Admin, KhachHang,Voucher
from werkzeug.security import generate_password_hash

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from discounts.test.pages.HomePage import HomePage


def create_app():  # pragma: no cover
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'templates')
    app = Flask(__name__,template_folder=template_dir)

    app.config.update({
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "PAGE_SIZE": 2,
        "SECRET_KEY": "^#@$*Juifdyfuhsfai#@&#^*",
        "CART_KEY": "cart",
    })
    db.init_app(app)
    login.init_app(app)

    from discounts.index import register_routes
    register_routes(app)

    return app

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_session(test_app):
    yield  db.session
    db.session.rollback()


# @pytest.fixture()
# def test_cloudinary(monkeypatch):
#     def fake_upload(file):
#         return{'secure_url':'https://fake-image.png'}
#
#     monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)

@pytest.fixture
def sample_users(test_session):
    user_admin = Admin(
        name="Admin",
        username="admin",
        password=generate_password_hash("123"),
        email="2351050211y@ou.edu.vn",
        user_role=1,
    )

    user_customer = KhachHang(
        name="Khách",
        username="khach",
        password=generate_password_hash("123"),
        email="nguyenhuynhnhuybt@gmail.com",
        user_role=0,
    )

    test_session.add_all([user_admin, user_customer])
    test_session.commit()

    yield {
        "user_admin": user_admin,
        "user_customer": user_customer
    }

@pytest.fixture
def sample_product(test_session):
    p1 = Product(name='Sua TH', price=30, category_id=1)
    p2 = Product(name='Mi goi Hao Hao', price=20, category_id=2)
    p3 = Product(name='Sua ong Tho', price=35, category_id=1)
    p4 = Product(name='Mi Indome', price=35, category_id=2)

    test_session.add_all([p1, p2, p3, p4])
    test_session.commit()

    yield [p1, p2, p3, p4]


@pytest.fixture
def sample_vouchers(test_session):
    now = datetime.datetime.now()

    v = Voucher(
        MaGG="SALE100",
        LoaiGG="FIXED",
        GiaTri=10000,
        DieuKien=100000,
        SoLuong=100,
        DaSuDung=0,
        NgayBD=now,
        NgayKT=now + datetime.timedelta(days=7),  # Kết thúc sau 1 tuần
        Hinhthuc="Shipping",
        DieuKienSP="1"
    )

    v_valid = Voucher(
        MaGG="VALID",
        LoaiGG="PERCENTAGE",
        GiaTri=10,
        DieuKien=0,
        SoLuong=10,
        DaSuDung=0,
        NgayBD=now - datetime.timedelta(days=1),
        NgayKT=now + datetime.timedelta(days=5),
        Hinhthuc="Shipping"
    )

    v_future = Voucher(
        MaGG="FUTURE",
        LoaiGG="PERCENTAGE",
        GiaTri=10,
        DieuKien=0,
        SoLuong=10,
        DaSuDung=0,
        NgayBD=now + datetime.timedelta(days=2),  # chưa tới hạn
        NgayKT=now + datetime.timedelta(days=10),
        Hinhthuc="Promotion"
    )

    v_expired = Voucher(
        MaGG="EXPIRED",
        LoaiGG="PERCENTAGE",
        GiaTri=10,
        DieuKien=0,
        SoLuong=10,
        DaSuDung=0,
        NgayBD=now - datetime.timedelta(days=10),
        NgayKT=now - datetime.timedelta(days=1),  # hết hạn
        Hinhthuc="Promotion"
    )

    test_session.add_all([v, v_valid, v_future, v_expired])
    test_session.commit()

    yield v, v_valid, v_future, v_expired


@pytest.fixture()
def mock_admin(monkeypatch):
    # bypass admin_required
    monkeypatch.setattr("discounts.index.admin_required", lambda f: f)

    # fake current_user
    class FakeUser:
        id = 1
        user_role = 1
        is_authenticated = True
    monkeypatch.setattr("flask_login.utils._get_user", lambda: FakeUser())

@pytest.fixture
def driver():
    service = Service(executable_path='../.venv/chromedriver.exe')
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

@pytest.fixture
def cart_ready(driver):
    home = HomePage(driver)
    home.open_page()
    home.add_to_cart()
    time.sleep(1)
    return driver