# File discounts/decorators.py
from functools import wraps

from flask import flash, redirect
from flask_login import current_user

from discounts.models import UserRole


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ép kiểu int để chắc chắn 0 != 1
        # Dùng getattr để lấy role an toàn hơn trong môi trường Mock
        role = getattr(current_user, 'user_role', -1)
        if not current_user.is_authenticated or role is None or int(role) != UserRole.ADMIN:
            flash("Không có quyền truy cập. Vui lòng đăng nhập với quyền Admin!", "danger")
            return redirect('/login')

        return f(*args, **kwargs)

    return decorated_function