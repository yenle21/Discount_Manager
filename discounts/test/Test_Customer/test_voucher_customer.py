from datetime import datetime, timedelta


def test_apply_voucher_no_cart(sample_voucher,test_client):
    with test_client.session_transaction() as sess:
        sess['cart'] = {}
    payload = {
        "voucher_id": sample_voucher.MaGG
    }
    response = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}', json=payload)
    assert response.status_code == 200
    # 2. Kiểm tra dữ liệu thực tế bên trong JSON
    data = response.get_json()
    assert data['status'] == 404
    assert data['message'] == "Giỏ hàng đang trống!"


def test_apply_voucher(test_client, test_session, sample_voucher):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Keo",
                "price": 500000,
                "quantity": 1,
                "category_id": 1
            }
        }
    payload = {
        "voucher_id": sample_voucher.MaGG
    }

    response = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}', json=payload)
    assert response.status_code == 200

    data = response.get_json()
    assert data.get('status') == 200
    assert data['applied_vouchers']['PROMOTION']['MaGG'] == sample_voucher.MaGG

# Test chưa đủ tiền tối thiểu
def test_apply_voucher_insufficient_total(test_client, test_session, sample_voucher):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Keo",
                "price": 50000,
                "quantity": 1,
                "category_id": 1
            }
        }

    res = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                          json={"voucher_id": sample_voucher.MaGG})
    data = res.get_json()
    assert data['status'] == 404
    assert "tối thiểu" in data['message']


# 2. Test sai danh mục sản phẩm
def test_apply_voucher_wrong_category(test_client, test_session, sample_voucher):
    #voucher yêu cầu danh mục "1"
    with test_client.session_transaction() as sess:
        # Sản phẩm trong giỏ thuộc danh mục "2"
        sess['cart'] = {"1": {"id": "1", "price": 500000, "quantity": 1, "category_id": 2}}

    res = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                          json={"voucher_id": sample_voucher.MaGG})
    data = res.get_json()
    assert data['status'] == 404
    assert "danh mục" in data['message']


def test_apply_voucher_mixed_cart_success(test_client, test_session, sample_voucher):
    sample_voucher.DieuKienSP = "1"
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"id": "1", "price": 100000, "quantity": 1, "category_id": "1"},  # Đúng cate
            "2": {"id": "2", "price": 100000, "quantity": 1, "category_id": "2"}  # Sai cate
        }

    res = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                          json={"voucher_id": sample_voucher.MaGG})
    assert res.get_json()['status'] == 200


def test_apply_voucher_not_found(test_client):
    with test_client.session_transaction() as sess:
        sess['cart'] = {"1": {"id": "1", "price": 500000, "quantity": 1}}

    # Gửi một mã không tồn tại
    res = test_client.put('/api/apply-voucher/INVALID_CODE',
                          json={"voucher_id": "INVALID_CODE"})
    data = res.get_json()
    assert data['status'] == 404
    assert "Mã không tồn tại" in data['message']
# Kiem tra ngay bat dau
def test_apply_voucher_upcoming(test_client, test_session, sample_voucher):

    sample_voucher.NgayBD = datetime.now() + timedelta(days=1)
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Keo",
                "price": 200000,
                "quantity": 1,
                "category_id": 1
            }
        }

    response = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                               json={"voucher_id": sample_voucher.MaGG})

    data = response.get_json()
    assert data['status'] == 404
    assert "chưa đến hạn sử dụng" in data['message']


# Kiem tra ma het han
def test_apply_voucher_expired(test_client, test_session, sample_voucher):
    sample_voucher.NgayKT = datetime.now() - timedelta(days=30)
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Keo",
                "price": 200000,
                "quantity": 1,
                "category_id": 1
            }
        }

    response = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                               json={"voucher_id": sample_voucher.MaGG})

    data = response.get_json()
    assert data['status'] == 404
    assert "Mã giảm giá này đã hết hạn sử dụng rồi" in data['message']
# kiếm tra số lượng voucher hiện tại so với lượt đã sử dụng
def test_apply_voucher_out_of_stock(test_client, test_session, sample_voucher):
    sample_voucher.SoLuong = 10
    sample_voucher.DaSuDung = 10
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Keo",
                "price": 200000,
                "quantity": 1,
                "category_id": 1
            }
        }

    response = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                               json={"voucher_id": sample_voucher.MaGG})

    data = response.get_json()
    assert data['status'] == 404
    assert "hết lượt sử dụng" in data['message']

# Khách hàng nhập mã mới đè lên mã cũ cùng loại
def test_apply_voucher_overwrite_existing(test_client, test_session, sample_voucher):
    sample_voucher.Hinhthuc = "Promotion"
    test_session.commit()

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Keo",
                "price": 200000,
                "quantity": 1,
                "category_id": "1"  # Dùng chuỗi '1' cho an toàn như đã fix
            }
        }

        sess['applied_vouchers'] = {
            'SHIPPING': {'MaGG': 'FREE_SHIP_CU', 'GiaTri': 15000},
            'PROMOTION': {'MaGG': 'MA_GIAM_GIA_CU', 'GiaTri': 10000}
        }

    res = test_client.put(f'/api/apply-voucher/{sample_voucher.MaGG}',
                          json={"voucher_id": sample_voucher.MaGG})

    data = res.get_json()
    assert data.get('status') == 200
    assert data['applied_vouchers']['PROMOTION']['MaGG'] == sample_voucher.MaGG
    assert data['applied_vouchers']['SHIPPING']['MaGG'] == 'FREE_SHIP_CU'