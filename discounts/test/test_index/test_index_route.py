def test_index_basic(test_client, monkeypatch):
    class FakeProduct:
        def __init__(self, name, price):
            self.name = name
            self.price = price

    # Mock data
    monkeypatch.setattr("discounts.dao.load_categories", lambda: ["cate1", "cate2"])
    monkeypatch.setattr(
        "discounts.dao.load_products",
        lambda **kwargs: [FakeProduct("SP1", 10000), FakeProduct("SP2", 20000)]
    )
    monkeypatch.setattr("discounts.dao.count_product", lambda **kwargs: 4)

    res = test_client.get('/')

    assert res.status_code == 200
    assert b"SP1" in res.data
    assert b"SP2" in res.data

def test_index_with_kw(test_client, monkeypatch):
    class FakeProduct:
        def __init__(self, name, price):
            self.name = name
            self.price = price

    monkeypatch.setattr("discounts.dao.load_categories", lambda: [])
    monkeypatch.setattr(
        "discounts.dao.load_products",
        lambda **kwargs: [FakeProduct("Sua TH", 10000)]
    )
    monkeypatch.setattr("discounts.dao.count_product", lambda **kwargs: 1)

    res = test_client.get('/?kw=Sua')

    assert res.status_code == 200
    assert b"Sua TH" in res.data

def test_index_with_category(test_client, monkeypatch):
    class FakeProduct:
        def __init__(self, name, price):
            self.name = name
            self.price = price

    monkeypatch.setattr("discounts.dao.load_categories", lambda: ["cate1"])
    monkeypatch.setattr(
        "discounts.dao.load_products",
        lambda **kwargs: [FakeProduct("Mi goi", 5000)]
    )
    monkeypatch.setattr("discounts.dao.count_product", lambda **kwargs: 1)

    res = test_client.get('/?category_id=1')

    assert res.status_code == 200
    assert b"Mi goi" in res.data

def test_index_pagination(test_client, monkeypatch):
    class FakeProduct:
        def __init__(self, name, price):
            self.name = name
            self.price = price

    monkeypatch.setattr("discounts.dao.load_categories", lambda: [])
    monkeypatch.setattr(
        "discounts.dao.load_products",
        lambda **kwargs: [FakeProduct("Page2", 20000)]
    )
    monkeypatch.setattr("discounts.dao.count_product", lambda **kwargs: 10)

    res = test_client.get('/?page=2')

    assert res.status_code == 200
    assert b"Page2" in res.data

def test_index_no_product(test_client, monkeypatch):
    monkeypatch.setattr("discounts.dao.load_categories", lambda: [])
    monkeypatch.setattr("discounts.dao.load_products", lambda **kwargs: [])
    monkeypatch.setattr("discounts.dao.count_product", lambda **kwargs: 0)

    res = test_client.get('/')

    assert res.status_code == 200

def test_index_with_cart(test_client, monkeypatch):
    class FakeProduct:
        def __init__(self, name, price):
            self.name = name
            self.price = price

    monkeypatch.setattr("discounts.dao.load_categories", lambda: [])
    monkeypatch.setattr(
        "discounts.dao.load_products",
        lambda **kwargs: [FakeProduct("SP1", 10000)]
    )
    monkeypatch.setattr("discounts.dao.count_product", lambda **kwargs: 1)

    with test_client.session_transaction() as sess:
        sess['cart'] = {
            "1": {"quantity": 2, "price": 10000},
            "2": {"quantity": 3, "price": 20000}
        }

    res = test_client.get('/')

    assert res.status_code == 200
