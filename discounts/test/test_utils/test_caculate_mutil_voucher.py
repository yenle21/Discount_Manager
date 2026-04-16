from discounts.utils import calculate_multi_vouchers


def test_calculate_multi_vouchers_combined():
    applied_vouchers = {
        "PROMOTION": {"GiaTri": 10},  # Giảm 10%
        "SHIPPING": {"GiaTri": 15000}  # Giảm 15k ship
    }
    total_price = 100000
    result = calculate_multi_vouchers(applied_vouchers, total_price)

    # 10% của 100k = 10k. 10k + 15k = 25k
    assert result["discount_amount"] == 25000
    assert result["new_price"] == 75000


def test_calculate_multi_vouchers_only_shipping():
    applied_vouchers = {
        "SHIPPING": {"GiaTri": 20000}
    }
    total_price = 100000
    result = calculate_multi_vouchers(applied_vouchers, total_price)
    assert result["discount_amount"] == 20000
    assert result["new_price"] == 80000


def test_calculate_multi_vouchers_percent_over_100():
    # Test logic: nếu GiaTri >= 100 thì coi như giảm số tiền mặt (theo code bạn viết)
    applied_vouchers = {
        "PROMOTION": {"GiaTri": 200}
    }
    total_price = 1000
    result = calculate_multi_vouchers(applied_vouchers, total_price)
    assert result["discount_amount"] == 200
    assert result["new_price"] == 800