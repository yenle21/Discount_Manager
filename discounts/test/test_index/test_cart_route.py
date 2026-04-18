from datetime import datetime


def test_cart_route(test_client,mocker):
    class FakeCart:
        def __init__(self):
            self.total_quantity = 0
            self.total_price = 0
    mock_update = mocker.patch("discounts.dao.get_all_vouchers_active")
    mock_add = mocker.patch("discounts.utils.cart_stash",return_value=FakeCart())

    res = test_client.get("/cart")
    assert res.status_code == 200

def test_cart_voucher_split(test_client, mocker):
    class FakeVoucher:
        def __init__(self, hinhthuc):
            self.Hinhthuc = hinhthuc
            self.NgayKT = datetime.now()
            self.MaGG = hinhthuc
            self.MoTa = hinhthuc

    class FakeCart:
        def __init__(self):
            self.total_quantity = 0
            self.total_price = 0
    vouchers = [
        FakeVoucher("Promotion"),
        FakeVoucher("Discount"),
        FakeVoucher("Shipping"),
        FakeVoucher("Free Shipping")
    ]
    mocker.patch(
        "discounts.dao.get_all_vouchers_active",
       return_value=vouchers
    )
    mocker.patch(
        "discounts.utils.cart_stash",
       return_value=FakeCart()
    )
    res = test_client.get('/cart')
    assert res.status_code == 200
    assert b"Shipping" in res.data
    assert b"Promotion" in res.data

def test_cart_no_session(test_client, mocker):
    class FakeCart:
        def __init__(self):
            self.total_quantity = 0
            self.total_price = 0

    mocker.patch("discounts.utils.cart_stash", return_value=FakeCart())
    mocker.patch("discounts.dao.get_all_vouchers_active", return_value=[])

    res = test_client.get('/cart')
    html = res.data.decode("utf-8")

    assert "Giỏ hàng của bạn đang trống" in html

def test_cart_with_items(test_client, mocker):
    class FakeCart:
        def __init__(self):
            self.total_quantity = 2
            self.total_price = 20000

    mocker.patch(
        "discounts.utils.cart_stash",
        return_value=FakeCart()
    )

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                "id": "1",
                "name": "Mì Gói",
                "price": 10000,
                "quantity": 2,
                "image": "test.jpg",
                "category_id": 1
            }
        }

    res = test_client.get('/cart')

    assert res.status_code == 200
    with test_client.session_transaction() as sess:
        assert sess['cart']['1']['quantity'] == 2
        assert sess['cart']['1']['name'] == 'Mì Gói'

def test_cart_total_quantity_display(test_client, mocker):
    class FakeCart:
        def __init__(self):
            self.total_quantity = 5
            self.total_price = 100000

    mocker.patch("discounts.utils.cart_stash", return_value=FakeCart())
    mocker.patch("discounts.dao.get_all_vouchers_active", return_value=[])

    res = test_client.get('/cart')
    html = res.data.decode("utf-8")

    assert "5" in html

def test_cart_total_price_display(test_client, mocker):
    class FakeCart:
        def __init__(self):
            self.total_quantity = 1
            self.total_price = 50000

    mocker.patch("discounts.utils.cart_stash", return_value=FakeCart())
    mocker.patch("discounts.dao.get_all_vouchers_active", return_value=[])

    res = test_client.get('/cart')
    html = res.data.decode("utf-8")

    assert res.status_code == 200
    assert "50,000" in html

