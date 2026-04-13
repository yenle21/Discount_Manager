import pytest
from discounts.models import Product, Category
from discounts import dao
from discounts.test.test_base import test_session, test_app, test_client

# TC01: load_categories
def test_load_categories(test_session):
    c1 = Category(id=1, name="Sữa")
    c2 = Category(id=2, name="Bánh")

    test_session.add_all([c1, c2])
    test_session.commit()

    result = dao.load_categories()

    assert len(result) == 2
    assert result[0].name == "Sữa"


# TC02: load_products không filter
def test_load_products_all(test_session):
    p1 = Product(id=1, name="Sữa Vinamilk", price=10, category_id=1)
    p2 = Product(id=2, name="Bánh Oreo", price=5, category_id=2)

    test_session.add_all([p1, p2])
    test_session.commit()

    result = dao.load_products()

    assert len(result) == 2


# TC03: filter theo category
def test_load_products_by_category(test_session):
    p1 = Product(id=1, name="Sữa Vinamilk", price=10, category_id=1)
    p2 = Product(id=2, name="Bánh Oreo", price=5, category_id=2)

    test_session.add_all([p1, p2])
    test_session.commit()

    result = dao.load_products(cate_id=1)

    assert len(result) == 1
    assert result[0].category_id == 1


# TC04 - filter theo keyword
def test_load_products_by_keyword(test_session):
    p1 = Product(id=1, name="Sữa Vinamilk", price=10, category_id=1)
    p2 = Product(id=2, name="Bánh Oreo", price=5, category_id=2)

    test_session.add_all([p1, p2])
    test_session.commit()

    result = dao.load_products(kw="Sữa")

    assert len(result) == 1
    assert "Sữa" in result[0].name


# TC05 - phân trang
def test_load_products_pagination(test_session):
    for i in range(1, 11):
        test_session.add(Product(id=i, name=f"SP{i}", price=10, category_id=1))
    test_session.commit()

    result = dao.load_products(page=1)

    assert len(result) <= 8   # PAGE_SIZE mặc định


# TC06 - count_product
def test_count_product(test_session):
    test_session.add_all([
        Product(id=1, name="Sữa A", price=10, category_id=1),
        Product(id=2, name="Sữa B", price=10, category_id=1)
    ])
    test_session.commit()

    count = dao.count_product(cate_id=1)

    assert count == 2


# TC07 - get_product_by_id tồn tại
def test_get_product_by_id_found(test_session):
    p = Product(id=1, name="Sữa Vinamilk", price=10, category_id=1)
    test_session.add(p)
    test_session.commit()

    result = dao.get_product_by_id(1)

    assert result is not None
    assert result.name == "Sữa Vinamilk"


# TC08 - get_product_by_id không tồn tại
def test_get_product_by_id_not_found(test_session):
    result = dao.get_product_by_id(999)

    assert result is None


def test_add_to_cart(test_client):
    # Gửi dữ liệu giả lập lên giỏ hàng
    res = test_client.post('/api/cart', json={
        "id": "1", "name": "Sữa", "price": 15000, "image": "https://link-anh-ao.com/sua.jpg", "quantity": 1
    })

    assert res.status_code == 200
    # Kiểm tra xem dữ liệu có nằm trong session không
    with test_client.session_transaction() as sess:
        assert '1' in sess['cart']
        assert sess['cart']['1']['quantity'] == 1