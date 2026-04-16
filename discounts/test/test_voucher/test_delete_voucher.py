import json

from discounts.test.conftest import test_client,test_app

from discounts.test.conftest import test_client,test_app, mock_admin

#TC1: Không phải ADMIN
def test_delete_voucher_not_admin(test_client, monkeypatch):
    class FakeUser:
        user_role = 2  # không phải admin
        is_authenticated = True
    monkeypatch.setattr("flask_login.utils._get_user", lambda: FakeUser())

    res = test_client.get('/delete_voucher/1')
    data = json.loads(res.data)

    assert res.status_code == 200
    assert data["status"] == 403


#TC2: Voucher không tồn tại
def test_delete_voucher_not_found(test_client, mock_admin, monkeypatch):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    res = test_client.get('/delete_voucher/1', follow_redirects=True)

    assert res.status_code == 200
    assert b"Voucher" in res.data


#TC3: Voucher đã sử dụng
# def test_delete_voucher_already_used(test_client, mock_admin, monkeypatch):
#     class Voucher:
#         DaSuDung = 5
#
#     monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: Voucher())
#
#     deleted = {"called": False}
#
#     monkeypatch.setattr("discounts.db.session.delete", lambda x: deleted.update({"called": True}))
#
#     res = test_client.get('/delete_voucher/1', follow_redirects=True)
#
#     assert res.status_code == 200
#     assert deleted["called"] is False


#TC4: Xóa thành công
def test_delete_voucher_success(test_client, mock_admin, monkeypatch):
    class Voucher:
        DaSuDung = 0

    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: Voucher())

    deleted = {"called": False}

    def fake_delete(obj):
        deleted["called"] = True

    monkeypatch.setattr("discounts.db.session.delete", fake_delete)
    monkeypatch.setattr("discounts.db.session.commit", lambda: None)

    res = test_client.get('/delete_voucher/1', follow_redirects=True)

    assert res.status_code == 200
    assert deleted["called"] is True


#TC5: Lỗi hệ thống
def test_delete_voucher_exception(test_client, mock_admin, monkeypatch):
    class Voucher:
        DaSuDung = 0

    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: Voucher())

    rollback_called = {"called": False}

    monkeypatch.setattr(
        "discounts.db.session.delete",
        lambda x: (_ for _ in ()).throw(Exception("DB Error"))
    )
    monkeypatch.setattr(
        "discounts.db.session.rollback",
        lambda: rollback_called.update({"called": True})
    )

    res = test_client.get('/delete_voucher/1', follow_redirects=True)

    assert res.status_code == 200
    assert rollback_called["called"] is True  # 👈 check rollback