
def test_add_to_cart(test_client):
    res = test_client.post('/api/cart', json={
        'id':1,
        'name':'Sua TH',
        'price':100,
        'image': 'https://hinh-anh.png'
    })

    assert res.status_code == 200
    data = res.get_json()
    assert data['total_quantity'] == 1
    assert data['total_price'] == 100

def test_add_to_cart_increase_item(test_client):
    test_client.post('/api/cart', json={
        'id': 1,
        'name': 'Sua TH',
        'price': 100,
        'image': 'https://hinh-anh.png'
    })
    res = test_client.post('/api/cart', json={
        'id': 2,
        'name': 'Mi goi',
        'price': 50,
        'image': 'https://hinh-anh2.png'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_quantity'] == 2
    assert data['total_price'] == 150

def test_add_to_cart_existing_item(test_client):
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

    res = test_client.post('/api/cart', json={
        'id': 1,
        'name': 'Mi goi',
        'price': 50,
        'image': 'https://hinh-anh2.png'
    })
    assert res.status_code == 200

    data = res.get_json()
    assert data['total_quantity'] == 3
    assert data['total_price'] == 150
    with test_client.session_transaction() as session:
        cart = session['cart']

        assert len(cart) == 1
        assert "1" in cart

def test_update_cart_sucess(test_client):
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
    res = test_client.put('/api/cart/1', json={
        'quantity': 6
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_quantity'] == 6
    assert data['total_price'] == 300
    with test_client.session_transaction() as session:
        cart = session['cart']
        assert len(cart) == 1
        assert cart['1']['quantity'] == 6

def test_update_cart_invalid_data(test_client):
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
    res = test_client.put('/api/cart/1', json={'quantity': 'abc'})
    assert res.status_code == 400


def test_update_cart_no_item(test_client):
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
    res = test_client.put('/api/cart/100', json={
        'quantity': 6
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_quantity'] == 2
    assert data['total_price'] == 100
    with test_client.session_transaction() as session:
        cart = session['cart']
        assert len(cart) == 1
        assert cart['1']['quantity'] == 2


def test_update_cart_to_zero(test_client):
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

    # Cập nhật số lượng về 0
    res = test_client.put('/api/cart/1', json={'quantity': 0})

    assert res.status_code == 200
    with test_client.session_transaction() as session:
        cart = session['cart']
        # Kiểm tra xem sản phẩm đã bị xóa khỏi giỏ hàng chưa
        assert "1" not in cart
        assert len(cart) == 0

def test_delete(test_client):
   test_client.delete('/api/cart/1')
   with test_client.session_transaction() as session:
       assert session.get('cart') is None
def test_delete_to_cart(test_client):
    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {
                'id': "1",
                'name': 'Bot giat 01',
                'price': 50,
                'quantity': 1,
                'image': 'https://hinh-anh2.png'
            },   "2": {
                'id': "2",
                'name': 'Bot Giat 02',
                'price': 60,
                'quantity': 1,
                'image': 'https://hinh-anh2.png'
            }
        }
    res = test_client.delete('/api/cart/1')

    with test_client.session_transaction() as session:
        cart = session['cart']
        assert cart is not None
        assert  '1'  not in cart
        assert '2' in cart
        assert len(cart) == 1
        data = res.get_json()
        assert data['total_quantity'] == 1
        assert data['total_price'] == 60