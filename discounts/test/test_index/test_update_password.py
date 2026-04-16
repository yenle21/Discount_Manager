from discounts.dao import update_password


def test_verify_reset_success(test_client, mocker):
    # giả lập OTP đã lưu
    from discounts.index import otp_storage
    otp_storage["yen@gmail.com"] = "123456"

    # mock update password thành công
    mocker.patch("discounts.dao.update_password", return_value=True)

    payload = {
        "email": "yen@gmail.com",
        "otp": "123456",
        "new_password": "Abc@1234"
    }

    res = test_client.post("/api/verify-reset", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True
    assert "thành công" in data["message"]

def test_verify_reset_fail_wrong_otp(test_client, mocker):
    from discounts.index import otp_storage
    otp_storage["yen@gmail.com"] = "123456"

    payload = {
        "email": "yen@gmail.com",
        "otp": "000000",   # sai OTP
        "new_password": "Abc@1234"
    }

    res = test_client.post("/api/verify-reset", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is False
    assert "OTP không đúng" in data["message"]

def test_verify_reset_fail_no_otp(test_client):
    payload = {
        "email": "notfound@gmail.com",
        "otp": "123456",
        "new_password": "Abc@1234"
    }

    res = test_client.post("/api/verify-reset", json=payload)
    data = res.get_json()

    assert data["success"] is False
    assert "OTP không đúng" in data["message"]

def test_verify_reset_fail_invalid_password(test_client, mocker):
    from discounts.index import otp_storage
    otp_storage["yen@gmail.com"] = "123456"

    payload = {
        "email": "yen@gmail.com",
        "otp": "123456",
        "new_password": "abc123"   # ❌ không đủ điều kiện
    }

    res = test_client.post("/api/verify-reset", json=payload)
    data = res.get_json()

    assert data["success"] is False
    assert "Mật khẩu phải có ít nhất" in data["message"]

def test_verify_reset_fail_update_password(test_client, mocker):
    from discounts.index import otp_storage
    otp_storage["yen@gmail.com"] = "123456"

    # giả lập lỗi DB
    mocker.patch("discounts.dao.update_password", return_value=False)

    payload = {
        "email": "yen@gmail.com",
        "otp": "123456",
        "new_password": "Abc@1234"
    }

    res = test_client.post("/api/verify-reset", json=payload)
    data = res.get_json()

    assert data["success"] is False
    assert "Lỗi hệ thống" in data["message"]


def test_update_password_db_error(mocker):
    #Giả lập tìm thấy user
    mock_user = mocker.Mock()
    mocker.patch("discounts.dao.get_user_by_email", return_value=mock_user)

    #Giả lập lỗi khi commit (ví dụ mất kết nối database)
    mocker.patch("discounts.db.session.commit", side_effect=Exception("DB Error"))
    mock_rollback = mocker.patch("discounts.db.session.rollback")
    result = update_password("yenbaole@gmail.com", "Moi123@")
    assert result is False

    mock_rollback.assert_called_once()