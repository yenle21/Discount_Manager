from unittest.mock import patch
from discounts.models import Voucher
from discounts.models import UserRole
from discounts.test.conftest import test_client,test_app

def test_admin_create_success(test_client,test_app):

    # gia lap dang nhap voi role la Admin
    fake_user = type("User", (), {
        "is_authenticated": True,
        "user_role": UserRole.ADMIN,
        "id": 1
    })()

    with patch("flask_login.utils._get_user", return_value=fake_user):

        res = test_client.post('/add', data={
            "MaGG": "MGG001",
            "Hinhthuc": "online",
            "LoaiGG": "percent",
            "GiaTri": 10,
            "SoLuong": 5,
            "NgayBD": "2026-04-01T00:00",
            "NgayKT": "2026-04-30T23:59",
            "TrangThai": "Active",
            "MoTa": "Test voucher",
            "admin_id": 1,
            "DieuKien": 100000,
            "DieuKienSP": "ALL"
        })

        # kiểm tra redict
        assert res.status_code == 302
        assert "/admin" in res.location
        # kiểm tra DB
        with test_app.app_context():
            voucher = Voucher.query.filter_by(MaGG="MGG001").first()
            assert voucher is not None
            assert voucher.GiaTri == 10
            assert voucher.SoLuong == 5


def test_client_create_fail(test_client):
    fake_user = type("User", (), {
        "is_authenticated": True,
        "user_role": UserRole.KHACHHANG,
        "id": 2
    })()

    with patch("flask_login.utils._get_user", return_value=fake_user):
        res = test_client.post('/add', data={})

        assert res.status_code == 302
        assert "/" in res.location

def test_create_not_login(test_client):
    fake_user = type("User", (), {
        "is_authenticated": False #ko cần giả lập đăng nhập
    })()

    with patch("flask_login.utils._get_user", return_value=fake_user):
        res = test_client.post('/add', data={})
        assert res.status_code == 302
        assert "/login" in res.location

def test_duplicate_voucher(test_client,test_app):
    fake_user = type("User", (), {
        "is_authenticated": True,
        "user_role": UserRole.ADMIN,
        "id": 1
    })()

    with patch("flask_login.utils._get_user", return_value=fake_user):
        data = {
            "MaGG": "DISCOUNT10",
            "Hinhthuc": "shipping",
            "LoaiGG": "tiền",
            "GiaTri": 10,
            "SoLuong": 5,
            "NgayBD": "2026-04-01T00:00",
            "NgayKT": "2026-04-30T23:59",
            "TrangThai": "active",
            "MoTa": "Test voucher",
            "admin_id": 1,
            "DieuKien": 100000,
            "DieuKienSP": "ALL"
        }
        # tạo voucher lần đầu
        res1 = test_client.post('/add', data=data)
        assert res1.status_code == 302
        # tạo voucher lần 2 bị trùng
        res2 = test_client.post('/add', data=data)
        assert res2.status_code == 302
        assert "/create" in res2.location

        with test_app.app_context():
            vouchers = Voucher.query.filter_by(MaGG="DISCOUNT10").all()
            assert len(vouchers) == 1

def test_missing_magg(test_client,test_app):
    fake_user = type("User", (), {
        "is_authenticated": True,
        "user_role": UserRole.ADMIN,
        "id": 1
    })()

    with patch("flask_login.utils._get_user", return_value=fake_user):
        data = {
            "MaGG": "",
            "Hinhthuc": "shipping",
            "LoaiGG": "tiền",
            "GiaTri": 10,
            "SoLuong": 5,
            "NgayBD": "2026-04-01T00:00",
            "NgayKT": "2026-04-30T23:59",
            "TrangThai": "active",
            "MoTa": "Test voucher",
            "admin_id": 1,
            "DieuKien": 100000,
            "DieuKienSP": "ALL"
        }

        res = test_client.post('/add', data=data)
        assert res.status_code == 302
        assert "/create" in res.location

        with test_app.app_context():
            vouchers = Voucher.query.filter_by(MaGG="").all()
            assert len(vouchers) == 0
