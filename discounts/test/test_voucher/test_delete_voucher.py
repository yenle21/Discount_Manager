from discounts.test.conftest import test_client, mock_admin


# TC1: Không phải ADMIN
def test_delete_voucher_not_admin(test_client, mocker):
    class FakeUser:
        user_role = 2
        is_authenticated = True

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    assert "Bạn không có quyền".encode('utf-8') in res.data


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

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    res = test_client.post('/delete/USED123', follow_redirects=True)

    assert res.status_code == 200
    assert res.request.path == "/admin"

    expected_msg = "Không thể xóa mã USED123 vì đã có 5 lượt sử dụng!"
    assert expected_msg.encode('utf-8') in res.data


# TC4: Xóa thành công
def test_delete_voucher_success(test_client, mock_admin, mocker):
    class MockVoucher:
        MaGG = "SALE10"
        DaSuDung = 0

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
        DaSuDung = 0

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mocker.patch(
        "discounts.index.db.session.delete",
        side_effect=Exception("DB Error")
    )

    mock_rollback = mocker.patch("discounts.index.db.session.rollback")

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    mock_rollback.assert_called_once()
    assert "Lỗi hệ thống: DB Error".encode('utf-8') in res.data


# TC6: Chưa login
def test_delete_voucher_no_login(test_client, mocker):
    class FakeUser:
        is_authenticated = False

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    res = test_client.post('/delete/SALE10')

    assert res.status_code in (401, 302)  # tùy app bạn config