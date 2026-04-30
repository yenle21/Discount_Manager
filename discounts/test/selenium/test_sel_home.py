def test_add_to_cart_success(test_client, app):
    key = app.config['CART_KEY']

    res = test_client.post("/api/cart", json={
        "id": 1,
        "name": "Sữa tươi",
        "price": 50000,
        "image": "milk.jpg",
        "category_id": 1
    })

    data = res.get_json()
    print("RESPONSE:", data)

    assert res.status_code == 200
    assert data["status"] == 200

    # check session
    with test_client.session_transaction() as sess:
        cart = sess.get(key, {})
        assert "1" in cart
        assert cart["1"]["quantity"] == 1