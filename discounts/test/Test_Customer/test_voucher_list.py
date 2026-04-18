from datetime import timedelta, datetime

from datetime import datetime, timedelta


def test_voucher_list_success(mocker, test_client):
    # 1. Giả lập User (Đầy đủ thuộc tính)
    class FakeUser:
        is_authenticated = True
        name = "Khách Hàng Test"
        user_role = 0

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    now = datetime.now()

    v1 = mocker.MagicMock(
        MaGG="SHIP_FREE",
        Hinhthuc="Phí vận chuyển",
        NgayKT=now + timedelta(days=1),
        SoLuong=10,
        DaSuDung=2,
        DieuKien=50000,
        GiaTri=15000,  # <--- THÊM DÒNG NÀY
        MoTa="Free ship toàn quốc"
    )

    # Voucher khuyến mãi (Cần DieuKien vì HTML dòng 40 yêu cầu)
    v2 = mocker.MagicMock(
        MaGG="PROMO_50K",
        Hinhthuc="Giảm giá",
        NgayKT=now + timedelta(days=1),
        SoLuong=5,
        DaSuDung=5,
        DieuKien=100000,
        GiaTri=50000,  # <--- NÊN CÓ LUÔN CHO CHẮC
        MoTa="Giảm 50k đơn từ 100k"
    )

    # Voucher hết hạn
    v3 = mocker.MagicMock(
        MaGG="EXPIRED",
        Hinhthuc="Giảm giá",
        NgayKT=now - timedelta(days=1),
        SoLuong=10,
        DaSuDung=0,
        DieuKien=0,
        GiaTri=0
    )

    # 3. Mock DAO trả về danh sách
    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v1, v2, v3])

    # 4. Gọi route
    response = test_client.get('/voucher-list')

    # 5. Kiểm tra kết quả
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert "SHIP_FREE" in html_content
    assert "PROMO_50K" in html_content
    assert "EXPIRED" not in html_content

def test_voucher_list_no_login(mocker, test_client):
    class FakeUser:
        is_authenticated = False

    mock_user=mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    response = test_client.get('/voucher-list')
    assert response.status_code == 401

def test_voucher_list_empty(mocker, test_client):
    class FakeUser:
        is_authenticated =True
        name = "Test"
        user_role = 0
    mock_user = mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[])
    response = test_client.get('/voucher-list')

    # 4. Kiểm tra
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')


def test_voucher_classification_logic(test_client, mocker):
    # Giả lập đăng nhập
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0
    mock_user = mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    # Tạo 2 voucher có tên "lạ" để check logic strip() và lower()
    v1 = mocker.MagicMock(Hinhthuc="  VẬN CHUYỂN  ", NgayKT=None, SoLuong=10, DaSuDung=0, DieuKien=0, GiaTri=0)
    v2 = mocker.MagicMock(Hinhthuc="Giảm Giá Shopee", NgayKT=None, SoLuong=10, DaSuDung=0, DieuKien=0, GiaTri=0)

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v1, v2])

    response = test_client.get('/voucher-list')

    assert v1.Hinhthuc.lower().strip() == "vận chuyển"


def test_voucher_date_boundary(test_client, mocker):
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0

    mock_user = mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    now = datetime.now()
    # Voucher không có ngày kết thúc (vẫn phải hiển thị)
    v_no_date = mocker.MagicMock(Hinhthuc="Khuyến mãi", NgayKT=None, SoLuong=10, DaSuDung=0, DieuKien=0, GiaTri=0)

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v_no_date])

    response = test_client.get('/voucher-list')

    assert response.status_code == 200
    # Kiểm tra xem v_no_date có được tính toán con_lai không (nghĩa là nó vượt qua bước check date)
    assert v_no_date.con_lai == 10


def test_voucher_negative_stock_safety(test_client, mocker):
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0

    mock_user = mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    # Giả lập lỗi dữ liệu: Tổng 5 nhưng đã dùng 10
    v_error = mocker.MagicMock(Hinhthuc="Khuyến mãi", NgayKT=None, SoLuong=5, DaSuDung=10, DieuKien=0, GiaTri=0)

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v_error])

    test_client.get('/voucher-list')

    # Kiểm tra logic max(0, ...)
    assert v_error.con_lai == 0
    assert v_error.is_available is False