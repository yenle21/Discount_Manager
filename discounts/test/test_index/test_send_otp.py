def test_send_otp_success(test_client, mocker):
    class FakeUser:
        name = "Lê Bảo Yến"
        email = "yen@gmail.com"
    mocker.patch("discounts.dao.get_user", return_value=FakeUser())
    #tham số create=True để vượt qua lỗi AttributeError
    mock_mail = mocker.patch("discounts.index.mail", create=True)
    mock_mail.send.return_value = None

    payload = {
        "username": "baoyen",
        "email": "yen@gmail.com"
    }

    res = test_client.post("/api/send-otp", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is True

def test_send_otp_fail_invalid(test_client, mocker):
    # user không tồn tại
    mocker.patch("discounts.dao.get_user", return_value=None)

    payload = {
        "username": "baoyen",
        "email": "sai@gmail.com"
    }

    res = test_client.post("/api/send-otp", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is False
    assert "không khớp" in data["message"]

def test_send_otp_exception(test_client, mocker):
    class FakeUser:
        name = "Bảo Yến"

    # mock user hợp lệ
    mocker.patch("discounts.dao.get_user", return_value=FakeUser())

    # giả lập lỗi khi gửi mail

    mocker.patch("discounts.index.mail.send", side_effect=Exception("SMTP error"), create=True)

    payload = {
        "username": "baoyen",
        "email": "yen@gmail.com"
    }

    res = test_client.post("/api/send-otp", json=payload)
    data = res.get_json()

    assert res.status_code == 200
    assert data["success"] is False
    assert "Lỗi hệ thống" in data["message"]