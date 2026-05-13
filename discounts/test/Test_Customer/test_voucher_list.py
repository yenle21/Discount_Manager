from datetime import datetime, timedelta


def test_voucher_list_success(mocker, test_client):
    # 1. Giả lập User
    class FakeUser:
        is_authenticated = True
        name = "Khách Hàng Test"
        user_role = 0

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    now = datetime.now()

    # Voucher vận chuyển còn hạn, còn lượt dùng
    v1 = mocker.MagicMock(
        MaGG="SHIP_FREE",
        Hinhthuc="Phí vận chuyển",
        NgayBD=now - timedelta(days=5),   # đã bắt đầu
        NgayKT=now + timedelta(days=1),
        TrangThai="active",
        SoLuong=10,
        DaSuDung=2,
        DieuKien=50000,
        GiaTri=15000,
        MoTa="Free ship toàn quốc"
    )

    # Voucher khuyến mãi còn hạn nhưng hết lượt dùng
    v2 = mocker.MagicMock(
        MaGG="PROMO_50K",
        Hinhthuc="Giảm giá",
        NgayBD=now - timedelta(days=3),   # đã bắt đầu
        NgayKT=now + timedelta(days=1),
        TrangThai="active",
        SoLuong=5,
        DaSuDung=5,
        DieuKien=100000,
        GiaTri=50000,
        MoTa="Giảm 50k đơn từ 100k"
    )

    # Voucher hết hạn → không được hiển thị
    v3 = mocker.MagicMock(
        MaGG="EXPIRED",
        Hinhthuc="Giảm giá",
        NgayBD=now - timedelta(days=10),  # đã bắt đầu
        NgayKT=now - timedelta(days=1),   # đã hết hạn
        TrangThai="expired",
        SoLuong=10,
        DaSuDung=0,
        DieuKien=0,
        GiaTri=0
    )

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v1, v2, v3])

    response = test_client.get('/voucher-list')

    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert "SHIP_FREE" in html_content
    assert "PROMO_50K" in html_content
    assert "EXPIRED" not in html_content


def test_voucher_list_no_login(mocker, test_client):
    class FakeUser:
        is_authenticated = False

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    response = test_client.get('/voucher-list')
    assert response.status_code == 401


def test_voucher_list_empty(mocker, test_client):
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("discounts.dao.get_all_vouchers", return_value=[])

    response = test_client.get('/voucher-list')

    assert response.status_code == 200


def test_voucher_classification_logic(test_client, mocker):
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    now = datetime.now()

    # Tạo 2 voucher có Hinhthuc "lạ" để kiểm tra logic strip() và lower()
    v1 = mocker.MagicMock(
        Hinhthuc="  VẬN CHUYỂN  ",
        NgayBD=now - timedelta(days=1),   # đã bắt đầu
        NgayKT=None,
        TrangThai="active",
        SoLuong=10,
        DaSuDung=0,
        DieuKien=0,
        GiaTri=0
    )
    v2 = mocker.MagicMock(
        Hinhthuc="Giảm Giá Shopee",
        NgayBD=now - timedelta(days=1),   # đã bắt đầu
        NgayKT=None,
        TrangThai="active",
        SoLuong=10,
        DaSuDung=0,
        DieuKien=0,
        GiaTri=0
    )

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v1, v2])

    response = test_client.get('/voucher-list')

    assert response.status_code == 200
    assert v1.Hinhthuc.lower().strip() == "vận chuyển"


def test_voucher_date_boundary(test_client, mocker):
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    now = datetime.now()

    # Voucher không có ngày kết thúc → vẫn phải hiển thị
    v_no_date = mocker.MagicMock(
        Hinhthuc="Khuyến mãi",
        NgayBD=now - timedelta(days=1),   # đã bắt đầu
        NgayKT=None,
        TrangThai="active",
        SoLuong=10,
        DaSuDung=0,
        DieuKien=0,
        GiaTri=0
    )

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v_no_date])

    response = test_client.get('/voucher-list')

    assert response.status_code == 200
    # v_no_date vượt qua bước check date → con_lai phải được tính
    assert v_no_date.con_lai == 10


def test_voucher_negative_stock_safety(test_client, mocker):
    class FakeUser:
        is_authenticated = True
        name = "Test"
        user_role = 0

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    now = datetime.now()

    # Giả lập lỗi dữ liệu: SoLuong=5 nhưng DaSuDung=10
    v_error = mocker.MagicMock(
        Hinhthuc="Khuyến mãi",
        NgayBD=now - timedelta(days=1),   # đã bắt đầu
        NgayKT=None,
        TrangThai="active",
        SoLuong=5,
        DaSuDung=10,
        DieuKien=0,
        GiaTri=0
    )

    mocker.patch("discounts.dao.get_all_vouchers", return_value=[v_error])

    test_client.get('/voucher-list')
    assert v_error.con_lai == 0
    assert v_error.is_available is False