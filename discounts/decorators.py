from functools import wraps
from flask import redirect, flash
from flask_login import current_user

from discounts.models import UserRole


def anonymous_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            # KIỂM TRA ROLE ĐỂ CHUYỂN HƯỚNG ĐÚNG CHỖ
            # (Logic này giống hệt lúc đăng nhập thành công)

            if current_user.user_role == UserRole.ADMIN:
                return redirect('/admin')  # Thay bằng đường dẫn trang Admin của bạn

            elif current_user.user_role == UserRole.KHACHHANG:
                return redirect('/')  # Thay bằng đường dẫn trang KHACH HÀNG


            # Trường hợp không xác định được role hoặc role khác
            return redirect('/')

        return f(*args, **kwargs)

    return decorated_func


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_role != UserRole.ADMIN:
            flash("Bạn không có quyền truy cập vào trang này!", "danger")
            return redirect('/login')

        return f(*args, **kwargs)

    return decorated_function