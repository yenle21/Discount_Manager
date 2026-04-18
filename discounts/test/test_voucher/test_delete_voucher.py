import json

from discounts.test.conftest import test_client,test_app

from discounts.test.conftest import test_client,test_app, mock_admin

#TC1: Không phải ADMIN
def test_delete_voucher_not_admin(test_client, mocker):
    class FakeUser:
        user_role = 2
        is_authenticated = True
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    assert "Bạn không có quyền".encode('utf-8') in res.data



def test_delete_voucher_not_found(test_client, mock_admin, mocker):
    mocker.patch("discounts.dao.get_voucher_by_id", return_value=None)

    res = test_client.post('/delete/1', follow_redirects=True)

    assert res.status_code == 200
    assert "Voucher không tồn tại!".encode('utf-8') in res.data


#TC3: Voucher đã sử dụng
def test_delete_voucher_already_used(test_client, mocker, mock_admin):
    # 1. Giả lập voucher tồn tại và ĐÃ CÓ lượt sử dụng
    class MockVoucher:
        MaGG = "USED123"
        DaSuDung = 5  # Số lượt dùng > 0

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    res = test_client.post('/delete/USED123', follow_redirects=True)

    assert res.status_code == 200
    assert res.request.path == "/admin"

    expected_msg = "Không thể xóa mã USED123 vì đã có 5 lượt sử dụng!"
    assert expected_msg.encode('utf-8') in res.data

#TC4: Xóa thành công
def test_delete_voucher_success(test_client, mock_admin, mocker):
    class MockVoucher:
        DaSuDung = 0

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    mock_delete = mocker.patch("discounts.index.db.session.delete")
    mocker.patch("discounts.index.db.session.commit")

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    mock_delete.assert_called_once()
    assert "Xóa thành công voucher SALE10!".encode('utf-8') in res.data

#TC5: Lỗi hệ thống
def test_delete_voucher_exception(test_client, mock_admin, mocker):
    class MockVoucher:
        DaSuDung = 0

    mocker.patch("discounts.index.dao.get_voucher_by_id", return_value=MockVoucher())

    #Giả lập db.session.delete quăng lỗi bằng side_effect
    mocker.patch("discounts.index.db.session.delete", side_effect=Exception("DB Error"))

    #Tạo spy cho rollback để kiểm tra xem nó có được gọi không
    mock_rollback = mocker.patch("discounts.index.db.session.rollback")

    res = test_client.post('/delete/SALE10', follow_redirects=True)

    assert res.status_code == 200
    mock_rollback.assert_called_once()
    assert "Lỗi hệ thống: DB Error".encode('utf-8') in res.data

def test_delete_voucher_no_login(test_client, mocker):
    # Giả lập user chưa đăng nhập (is_authenticated = False)
    class FakeUser:
        is_authenticated = False
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    res = test_client.post('/delete/SALE10')

    assert res.status_code == 401