import pytest
from discounts import dao

pytest_plugins = ["discounts.test.test_base"]

def test_get_voucher_by_id_success(test_app, sample_voucher):
    with test_app.app_context():
        v = dao.get_voucher_by_id("MA1")
        assert v is not None
        assert v.MaGG == "MA1"

def test_get_voucher_not_found(test_app, sample_voucher):
    with test_app.app_context():
        v = dao.get_voucher_by_id("KHONGTONTAI")
        assert v is None

def test_edit_MaGG(test_app, sample_voucher):
    with test_app.app_context():
        data = {
            "MaGG": "EDIT"
        }
        result = dao.update_voucher("MA1", data) #tìm thấy MA1 thì True
        assert result is True

        v = dao.get_voucher_by_id("MA1")
        assert v.MaGG == "MA1" # khóa chính không được đổi

