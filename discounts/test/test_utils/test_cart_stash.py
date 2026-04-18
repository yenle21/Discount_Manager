from discounts.utils import cart_stash


def test_cart_stash_success():
    cart = {
        "1": {"quantity": 2, "price": 50000},
        "2": {"quantity": 1, "price": 100000}
    }
    result = cart_stash(cart)
    assert result["total_quantity"] == 3
    assert result["total_price"] == 200000

def test_cart_stash_empty():
    result = cart_stash({})
    assert result["total_quantity"] == 0
    assert result["total_price"] == 0