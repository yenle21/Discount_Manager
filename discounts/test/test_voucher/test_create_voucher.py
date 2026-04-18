from unittest.mock import patch

from discounts.dao import add_voucher
from discounts.models import Voucher
from discounts.models import UserRole

from discounts.test.conftest import test_client,test_app

from discounts.test.conftest import test_client,test_app, mock_admin


def test_add_voucher_success(test_client, mocker,mock_admin):
    mocker.patch("discounts.dao.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.dao.add_voucher", return_value=True)

    data = {
        "MaGG": "SALE10",
        "GiaTri": "20000",
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-06-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert res.location.endswith("/admin")


def test_add_voucher_duplicate(test_client, mocker, mock_admin):
    # Giả lập mã đã tồn tại
    mocker.patch("discounts.index.get_voucher_by_id", return_value={"id": 1})
    data = {
        "MaGG": "SALE10",
        "NgayBD": "2026-05-18T10:00",
        "NgayKT": "2026-06-20T10:00",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "20000",
        "SoLuong": "100"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)

    assert res.status_code == 200
    assert res.request.path == "/create"
    assert "Mã voucher đã tồn tại!".encode('utf-8') in res.data


def test_add_voucher_empty_code(test_client, mocker, mock_admin):
    data = {
        "MaGG": "",  # Mã trống
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien"
    }

    # Dùng follow_redirects=True để kiểm tra thông báo
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert res.status_code == 200
    assert res.request.path == "/create"
    assert "Mã voucher không được để trống!".encode('utf-8') in res.data


def test_add_voucher_code_with_space(test_client, mocker, mock_admin):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)

    data = {
        "MaGG": "SALE 10",  # Mã chứa khoảng trắng ở giữa
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert res.status_code == 200
    assert res.request.path == "/create"
    assert "Mã voucher không hợp lệ!".encode('utf-8') in res.data


def test_add_voucher_special_char_code(test_client, mocker, mock_admin):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)

    data = {
        "MaGG": "SALE@10!",  # Mã vi phạm Regex
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)

    assert res.status_code == 200
    assert res.request.path == "/create"
    # Giờ thì assert này sẽ Pass vì code đã chạy tới dòng check Regex
    assert "Mã voucher không hợp lệ!".encode('utf-8') in res.data

def test_add_voucher_invalid_date(test_client, mocker,mock_admin):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)

    data = {
        "MaGG": "SALE10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "20000",
        "SoLuong": "100",
        "NgayBD": "2026-04-20T10:00",  # Ngày bắt đầu
        "NgayKT": "2026-04-15T10:00"  # Ngày kết thúc (Nhỏ hơn ngày bắt đầu -> Lỗi)
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu!".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_past_end_day(test_client, mocker,mock_admin):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)

    data = {
        "MaGG": "SALE10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "20000",
        "SoLuong": "100",
        "NgayBD": "2026-01-20T10:00",
        "NgayKT": "2026-01-21T10:00" # Ngày kết thúc ở quá khứ
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Ngày kết thúc không được ở quá khứ!".encode('utf-8') in res.data
    assert res.status_code == 200

def test_add_voucher_past_start_date(test_client, mocker,mock_admin):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)

    data = {
        "MaGG": "SALE10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "20000",
        "SoLuong": "100",
        "NgayBD": "2026-01-20T10:00",  # Ngày bắt đầu ở quá khứ
        "NgayKT": "2026-04-21T10:00"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Ngày bắt đầu không được ở quá khứ!".encode('utf-8') in res.data
    assert res.status_code == 200

def test_add_voucher_negative_discount(test_client, mocker,mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id",return_value=None)

    data = {
        "MaGG": "PERCENT60",
        "LoaiGG": "tien",
        "GiaTri": "-10",  # Lỗi: giá trị âm
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_invalid_percent_range(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id",return_value=None)
    data = {
        "MaGG": "TEST",
        "LoaiGG": "phantram",
        "GiaTri": "60", # Lỗi: > 50
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
         "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Phần trăm giảm giá phải từ 1 đến 50!".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_negative_quantity(test_client, mocker,mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id",return_value=None)

    data = {
        "MaGG": "TEST",
        "LoaiGG": "phantram",
        "GiaTri": "20",
        "SoLuong": "-10", #số lượng âm
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Số lượng không hợp lệ".encode('utf-8') in res.data
    assert res.status_code == 200

def test_add_voucher_negative_condition(test_client, mocker,mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id",return_value=None)

    data = {
        "MaGG": "TEST",
        "LoaiGG": "phantram",
        "DieuKien": "-100",
        "GiaTri": "20",
        "SoLuong": "10", #số lượng âm
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Điều kiện không hợp lệ!".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_db_fail(test_client, mocker, mock_admin):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)

    # Patch hàm add_voucher trả về False để giả lập lỗi ghi vào Database
    mocker.patch("discounts.index.add_voucher", return_value=False)
    data = {
        "MaGG": "SALE2026",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "50000",
        "SoLuong": "100",
        "DieuKien": "100000",
        "DieuKienSP": "all",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data)
    #khi add_voucher trả về False, code sẽ redirect về /create
    assert res.status_code == 302
    assert res.location.endswith("/create")


def test_add_voucher_missing_info(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id")
    data = {
        "MaGG": "SALE10",
        "Hinhthuc": "", # Để trống
        "LoaiGG": "",    # Để trống
        "NgayBD": "2026-06-15T10:00",
        "NgayKT": "2026-07-20T10:00"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Vui lòng nhập đầy đủ thông tin".encode('utf-8') in res.data
    assert res.status_code == 200

def test_add_voucher_invalid_money_range(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id")
    data = {
        "MaGG": "CHEAP5K",
        "LoaiGG": "tien",
        "GiaTri": "5000", # Lỗi: < 10,000
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-06-15T10:00",
        "NgayKT": "2026-07-20T10:00"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_invalid_money_range_gt_cd(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id")
    data = {
        "MaGG": "CHEAP5K",
        "LoaiGG": "tien",
        "GiaTri": "30000000", # Lỗi: > 20,000,000
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-06-15T10:00",
        "NgayKT": "2026-07-20T10:00"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_quantity_over_limit(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id")
    data = {
        "MaGG": "MANY",
        "SoLuong": "1001", # Lỗi: > 1000
        "GiaTri": "20000",
        "LoaiGG": "tien",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-06-15T10:00",
        "NgayKT": "2026-07-20T10:00"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Số lượng không hợp lệ".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_data_type_error(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.get_voucher_by_id")
    data = {
        "MaGG": "ERROR1",
        "GiaTri": "abc",  # Mục tiêu test lỗi ép kiểu ở đây
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "NgayBD": "2026-06-01T10:00",
        "NgayKT": "2026-07-10T10:00"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Định dạng dữ liệu số hoặc ngày tháng không đúng!".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_space_2_dau(test_client, mocker, mock_admin):
    mocker.patch("discounts.dao.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.dao.add_voucher", return_value=True)
    #" SALE10 " thành "SALE10"
    data = {
        "MaGG": " SALE10 ",
        "GiaTri": "20000",
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-06-20T10:00"
    }
    res = test_client.post("/add", data=data)
    assert res.status_code == 302
    assert res.location.endswith("/admin")#strip thành công nên trả về trang admin

def test_add_voucher_only_end_date(test_client, mocker, mock_admin):
    mocker.patch("discounts.dao.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.dao.add_voucher", return_value=True)

    data = {
        "MaGG": "NOSTART",
        "GiaTri": "20000",
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "NgayBD": "",
        "NgayKT": "2026-12-31T23:59"
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc!".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_only_start_date(test_client, mocker, mock_admin):
    mocker.patch("discounts.dao.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.dao.add_voucher", return_value=True)

    data = {
        "MaGG": "NOEND",
        "GiaTri": "20000",
        "SoLuong": "10",
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "NgayBD": "2026-12-31T23:59",
        "NgayKT": ""
    }
    res = test_client.post("/add", data=data, follow_redirects=True)
    assert "Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc!".encode('utf-8') in res.data
    assert res.status_code == 200


def test_add_voucher_exception(test_client, mocker, mock_admin):
    mock_add = mocker.patch("discounts.dao.db.session.add", side_effect=Exception("Lỗi thêm voucher giả lập"))

    mock_rollback = mocker.patch("discounts.dao.db.session.rollback")

    fake_voucher_data = {
        "MaGG": "TEST_ERROR",
        "SoLuong": 10,
        "GiaTri": 50000
    }
    result = add_voucher(fake_voucher_data)

    assert result is False  # Phải trả về False vì đã rớt vào except
    mock_add.assert_called_once()  # Xác nhận hàm add đã chạy và gây lỗi
    mock_rollback.assert_called_once()  # Xác nhận đã gọi rollback để bảo vệ DB
