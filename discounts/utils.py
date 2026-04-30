
def cart_stash (cart):
    total_quantity, total_price = 0,0
    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_price += c['price']*c['quantity']

    return{
        "total_quantity": total_quantity,
        "total_price": total_price,
    }
def voucher_stash(applied_voucher, total_cart_price):
    discount_amount = 0
    total_cart_price = float(total_cart_price)

    if applied_voucher:
        loai_gg = str(applied_voucher.get('LoaiGG', '')).strip().lower()
        gia_tri = float(applied_voucher.get('GiaTri', 0))
        if 'tram' in loai_gg or 'trăm' in loai_gg or '%' in loai_gg:
            discount_amount = total_cart_price * (gia_tri / 100)

        else:
            discount_amount = gia_tri

        discount_amount = min(discount_amount, total_cart_price)


    return {
        "discount_amount": discount_amount,
        "new_price": total_cart_price - discount_amount
    }


def calculate_multi_vouchers(applied_vouchers, total_price):
    total_discount = 0

    # Duyệt qua các mã trong dictionary (SHIPPING, PROMOTION,...)
    for kind, v_info in applied_vouchers.items():
        gia_tri = v_info['GiaTri']

        if kind == 'PROMOTION':
            # Nếu là giảm theo % (ví dụ 50%)
            if gia_tri < 100:
                total_discount += total_price * (gia_tri / 100)
            else:
                total_discount += gia_tri

        elif kind == 'SHIPPING':
            if gia_tri < 100:
                total_discount += total_price * (gia_tri / 100)
            else:
                total_discount += gia_tri

    return {
        "discount_amount": total_discount,
        "total_price": total_price,  # Tổng tiền gốc
        "new_price": max(0, total_price - total_discount)  # Tổng thanh toán cuối cùng
    }