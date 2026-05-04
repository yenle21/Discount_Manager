from discounts.test.conftest import test_client, mock_admin

from datetime import datetime, timedelta

# TC1: Không phải ADMIN
def test_delete_voucher_not_admin(test_client, mocker):
    class FakeUser:
        user_role = 2
        is_authenticated = True

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    text = res.data.decode("utf-8")
    assert "Không có quyền" in text


# TC2: Không tồn tại
def test_delete_voucher_not_found(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=None)

    res = test_client.post('/delete/1', follow_redirects=True)

    assert res.status_code == 200
    assert "Voucher không tồn tại!".encode('utf-8') in res.data


# TC3: Voucher đã sử dụng
def test_delete_voucher_already_used(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "USED123"
        DaSuDung = 5
        SoLuong = 10
        NgayBD = datetime.now()
        NgayKT = datetime.now() + timedelta(days=3)

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    res = test_client.post('/delete/USED123', follow_redirects=True)

    assert res.status_code == 200
    assert res.request.path == "/admin"

    assert "Không thể xóa mã USED123" in res.get_data(as_text=True)


# TC4: Xóa thành công
def test_delete_voucher_success(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "SALE10"
        DaSuDung = 0
        SoLuong = 10
        NgayBD = datetime.now()
        NgayKT = datetime.now() + timedelta(days=3)

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mock_delete = mocker.patch("discounts.index.db.session.delete")
    mock_commit = mocker.patch("discounts.index.db.session.commit")

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    mock_delete.assert_called_once()
    mock_commit.assert_called_once()
    assert "Xóa thành công voucher SALE10!".encode('utf-8') in res.data


# TC5: Lỗi hệ thống
def test_delete_voucher_exception(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "SALE10"
        DaSuDung = 0
        SoLuong = 10
        NgayBD = datetime.now()
        NgayKT = datetime.now() + timedelta(days=3)

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mocker.patch(
        "discounts.index.db.session.delete",
        side_effect=Exception("DB Error")
    )

    mock_rollback = mocker.patch("discounts.index.db.session.rollback")

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    mock_rollback.assert_called_once()
    assert "Lỗi hệ thống" in res.get_data(as_text=True)


# TC6: Chưa login
def test_delete_voucher_no_login(test_client, mocker):
    class FakeUser:
        is_authenticated = False

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    res = test_client.post('/delete/SALE10')

    assert res.status_code in (401, 302)  # tùy app bạn config

# TC7: Voucher đang sử dụng dở (0 < DaSuDung < SoLuong) → KHÔNG cho xóa
def test_delete_voucher_partially_used(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "PARTIAL"
        DaSuDung = 3
        SoLuong = 10
        NgayBD = datetime.now()
        NgayKT = datetime.now() + timedelta(days=3)

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    res = test_client.post('/delete/PARTIAL', follow_redirects=True)

    assert res.status_code == 200
    assert "Không thể xóa mã PARTIAL".encode('utf-8') in res.data


# TC8: Voucher đã dùng hết (DaSuDung == SoLuong) → CHO xóa
def test_delete_voucher_fully_used(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "FULL"
        DaSuDung = 10
        SoLuong = 10
        NgayBD = datetime.now()
        NgayKT = datetime.now() + timedelta(days=3)

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mock_delete = mocker.patch("discounts.index.db.session.delete")
    mock_commit = mocker.patch("discounts.index.db.session.commit")

    res = test_client.post('/delete/FULL', follow_redirects=True)

    assert res.status_code == 200
    mock_delete.assert_called_once()
    mock_commit.assert_called_once()


# TC9: DaSuDung = None → coi như 0 → CHO xóa
def test_delete_voucher_null_usage(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "NULL"
        DaSuDung = None
        SoLuong = 10
        NgayBD = datetime.now()
        NgayKT = datetime.now() + timedelta(days=3)
    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mock_delete = mocker.patch("discounts.index.db.session.delete")
    mock_commit = mocker.patch("discounts.index.db.session.commit")

    res = test_client.post('/delete/NULL', follow_redirects=True)

    assert res.status_code == 200
    mock_delete.assert_called_once()
    mock_commit.assert_called_once()

# TC1đ: Voucher hết hạn → CHO xóa dù đang sử dụng
def test_delete_voucher_expired_even_if_used(test_client, mock_admin, mocker):
    from datetime import datetime, timedelta

    class MockVoucher:
        MaGG = "EXPIRED"
        DaSuDung = 5
        SoLuong = 10
        NgayKT = datetime.now() - timedelta(days=1)  # đã hết hạn

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mock_delete = mocker.patch("discounts.index.db.session.delete")
    mock_commit = mocker.patch("discounts.index.db.session.commit")

    res = test_client.post('/delete/EXPIRED', follow_redirects=True)

    assert res.status_code == 200
    mock_delete.assert_called_once()
    mock_commit.assert_called_once()
    text = res.data.decode("utf-8")
    assert "hết hạn" in text
