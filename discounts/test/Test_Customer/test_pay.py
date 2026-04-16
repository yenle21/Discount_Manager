from discounts.models import CTHD


def test_pay_no_cart(test_client,mocker):
    class FakeUser:
        is_authenticated = True

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    with test_client.session_transaction() as sess:
        sess['cart'] = {}

    response = test_client.post("/api/checkout")
    assert response.get_json().get('status') == 404
    assert response.get_json().get('message') == "Giỏ hàng trống!"

def test_pay_success(test_client,mocker):
    class FakeUser:
        is_authenticated = True
        name = "Bảo Yến"

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("discounts.index.current_user", new=FakeUser())

    class FakeOrder:
        id = 99
    mocker.patch("discounts.dao.add_receipt", return_value=FakeOrder())
    mocker.patch("discounts.utils.cart_stash", return_value={'total_price': 100})
    mocker.patch("discounts.utils.calculate_multi_vouchers", return_value={'new_price': 100})
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                'id': "1",
                'name': 'Bot giat',
                'price': 50,
                'quantity': 2,
                'image': 'https://hinh-anh2.png'
            }
        }

    payload = {
        "name": "Yenletest",
        "phone": "0123456789",
        "address": "VN ho chi minh",
        "payment_method": "Tiền mặt"
    }
    response = test_client.post("/api/checkout", json=payload)

    # 7. Kiểm tra kết quả trả về
    data = response.get_json()
    assert data.get('status') == 200
    assert "Đặt hàng thành công" in data.get('message')

    # 8. Kiểm tra xem giỏ hàng đã được dọn sạch trong Session chưa
    with test_client.session_transaction() as sess:
        assert sess.get('cart') == {}


def test_checkout_exception(test_client, mocker):
    class FakeUser:
        name = "Name"
        is_authenticated = True

    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())
    mocker.patch("discounts.index.current_user", new=FakeUser())

    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 100}}
    mocker.patch("discounts.dao.add_receipt", side_effect=Exception("Database Connection Error"))

    payload = {
        "name": "Bảo Yến",
        "phone": "0123456789",
        "address": "nha be hcm"  # không nhập địa chỉ
    }
    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    assert data['status'] == 500
    assert "Lỗi hệ thống" in data['message']

def test_checkout_missing_address(test_client, mocker):
    # Mock user đăng nhập để vượt qua login_required
    class FakeUser:
        name = "Name"
        is_authenticated = True
    mocker.patch("discounts.index.current_user", new=FakeUser())
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    # Giả lập giỏ hàng có đồ
    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 100, "quantity": 1}}

    # Gửi payload thiếu 'address' hoặc để trống
    payload = {
        "name": "Bảo Yến",
        "phone": "0123456789",
        "address": "" #không nhập địa chỉ
    }

    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    assert data['status'] == 400
    assert "đầy đủ" in data['message']

def test_checkout_missing_sdt(test_client, mocker):
    # Mock user đăng nhập để vượt qua login_required
    class FakeUser:
        name = "Name"
        is_authenticated = True
    mocker.patch("discounts.index.current_user", new=FakeUser())
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    # Giả lập giỏ hàng có đồ
    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 100, "quantity": 1}}

    # Gửi payload thiếu 'address' hoặc để trống
    payload = {
        "name": "Bảo Yến",
        "phone": "",
        "address": "nha be thanh pho HCM"
    }

    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    assert data['status'] == 400
    assert "đầy đủ" in data['message']

def test_checkout_missing_name(test_client, mocker):
    # Mock user đăng nhập để vượt qua login_required
    class FakeUser:
        name = "Name"
        is_authenticated = True
    mocker.patch("discounts.index.current_user", new=FakeUser())
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    # Giả lập giỏ hàng có đồ
    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 100, "quantity": 1}}

    # Gửi payload thiếu 'address' hoặc để trống
    payload = {
        "name": "",
        "phone": "0123456789",
        "address": "nha be thanh pho HCM"
    }

    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    assert data['status'] == 400
    assert "đầy đủ" in data['message']

def test_checkout_invalid_phone(test_client, mocker):
    class FakeUser:
        name = "Name"
        is_authenticated = True
    mocker.patch("discounts.index.current_user", new=FakeUser())
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 100}}

    payload = {
        "name": "Bảo Yến",
        "phone": "abc-123", # Số điện thoại chứa chữ
        "address": "TP.HCM"
    }

    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    # Kì vọng hệ thống báo lỗi 400
    assert data['status'] == 400
    assert "Số điện thoại" in data['message']


def test_checkout_phone_not_start_with_zero(test_client, mocker):
    class FakeUser:
        name = "Name"
        is_authenticated = True

    mocker.patch("discounts.index.current_user", new=FakeUser())
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 100}}

    payload = {
        "name": "Bảo Yến",
        "phone": "8412345678",  # KHÔNG BẮT ĐẦU BẰNG 0
        "address": "TP.HCM"
    }

    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    assert data['status'] == 400
    assert "không hợp lệ" in data['message']


def test_add_receipt_success(test_session, sample_voucher):
    from discounts import dao, models

    # 1. Chuẩn bị dữ liệu đầu vào giả lập
    user = models.User(
        name="Lê Bảo Yến",
        username="baoyen",
        password="123",
        email="yen@gmail.com"
    )
    test_session.add(user)
    test_session.commit()  # Lưu vào DB test # Lấy đại 1 user từ DB test
    fake_cart = {
        "1": {"id": "1", "name": "Sữa", "price": 20000, "quantity": 2}
    }
    fake_vouchers = {
        "PROMOTION": {"MaGG": sample_voucher.MaGG}
    }
    fake_info = {
        "name": "Bảo Yến",
        "phone": "0901234567",
        "address": "TP.HCM"
    }

    # 2. Gọi trực tiếp hàm trong DAO
    order = dao.add_receipt(
        cart=fake_cart,
        user=user,
        hinh_thuc_tt="Tiền mặt",
        applied_vouchers=fake_vouchers,
        total_after_discount=40000,
        receiver_info=fake_info
    )

    # 3. Assert để phủ code và kiểm tra dữ liệu
    assert order is not None
    assert order.id is not None
    assert order.khach_hang_id == user.id

    # Kiểm tra chi tiết hóa đơn (CTHD) có được tạo không
    all_cthds = CTHD.query.all()
    # Tìm cthd của đơn hàng vừa tạo bằng cách so sánh đối tượng
    cthd = next((c for c in all_cthds if c.don_hang_parent_ref == order), None)

    assert cthd is not None
    assert cthd.MaSP == 1
    assert cthd.SoLuong == 2


def test_add_receipt_with_invalid_voucher(test_session):
    from discounts import dao, models

    user = models.User(
        name="Lê Bảo Yến",
        username="baoyen",
        password="123",
        email="yen@gmail.com"
    )
    test_session.add(user)
    test_session.commit()  # Lưu vào DB test
    fake_cart = {"1": {"id": "1", "name": "Keo", "price": 1000, "quantity": 1}}

    # Giả lập voucher không tồn tại trong DB
    fake_vouchers = {"PROMOTION": {"MaGG": "VOUCHER_KHONG_TON_TAI"}}

    order = dao.add_receipt(
        cart=fake_cart,
        user=user,
        hinh_thuc_tt="Chuyển khoản",
        applied_vouchers=fake_vouchers,
        total_after_discount=1000,
        receiver_info={"name": "A", "phone": "0", "address": "B"}
    )

    assert order is not None  # Đơn hàng vẫn tạo nhưng voucher không được cập nhật

def test_checkout_fail_cannot_create_order(test_client, mocker):
    class FakeUser:
        name = "Name"
        is_authenticated = True

    mocker.patch("discounts.index.current_user", new=FakeUser())
    mocker.patch("flask_login.utils._get_user", return_value=FakeUser())

    # Giả lập giỏ hàng
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"id": "1", "price": 100, "quantity": 1}
        }


    mocker.patch("discounts.dao.add_receipt", return_value=None)

    mocker.patch("discounts.utils.cart_stash", return_value={'total_price': 100})
    mocker.patch("discounts.utils.calculate_multi_vouchers", return_value={'new_price': 100})

    payload = {
        "name": "Bảo Yến",
        "phone": "0123456789",
        "address": "TP.HCM",
        "payment_method": "Tiền mặt"
    }

    res = test_client.post('/api/checkout', json=payload)
    data = res.get_json()

    assert data['status'] == 500 or data['status'] == 400
    assert "không thể" in data['message'].lower() or "thất bại" in data['message'].lower()
