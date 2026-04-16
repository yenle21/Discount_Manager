from discounts.utils import voucher_stash


def test_voucher_stash_percent():
    voucher = {"LoaiGG": "phantram", "GiaTri": 10}
    total_price = 200000
    result = voucher_stash(voucher, total_price)
    assert result["discount_amount"] == 20000  # 10% của 200k
    assert result["new_price"] == 180000

def test_voucher_stash_fixed_amount():
    voucher = {"LoaiGG": "tien", "GiaTri": 30000}
    total_price = 200000
    result = voucher_stash(voucher, total_price)
    assert result["discount_amount"] == 30000
    assert result["new_price"] == 170000

def test_voucher_stash_max_discount():
    # Giảm giá không được vượt quá tổng tiền giỏ hàng
    voucher = {"LoaiGG": "tien", "GiaTri": 500000}
    total_price = 200000
    result = voucher_stash(voucher, total_price)
    assert result["discount_amount"] == 200000
    assert result["new_price"] == 0