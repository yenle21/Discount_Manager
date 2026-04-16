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
        if not current_user.is_authenticated:
            return redirect('/login')
        if int(role) != UserRole.ADMIN:
            flash("Bạn không có quyền truy cập vào trang này!", "danger")
            return redirect('/')

        return f(*args, **kwargs)

    return decorated_function