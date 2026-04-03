import re
import cloudinary
import cloudinary.uploader
from flask import redirect, flash, url_for
from flask import Flask, render_template
from flask_login import LoginManager, current_user, login_user, logout_user

from discounts import app, db, login
from discounts.models import UserRole

import json


from flask import Flask, render_template, request
import json

from discounts import dao, app
from discounts.dao import load_products, load_categories

# Đọc dữ liệu từ JSON
@app.route("/")
def index():
    # 1. Lấy cate_id từ URL (ví dụ: /?category_id=1)
    cate_id = request.args.get('category_id')


    # 2. Lấy keyword từ ô Search (ví dụ: /?kw=sua)
    # Lưu ý: 'kw' phải khớp với thuộc tính 'name' của thẻ <input> trong HTML
    kw = request.args.get('kw')

    categories = dao.load_categories()

    # 3. Truyền cả cate_id và kw vào hàm load
    products = dao.load_products(cate_id=cate_id, kw=kw)

    return render_template('customer/customer.html',
                           categories=categories,
                           products=products)
@app.route("/cart")
def cart():
    # Load danh mục để Sidebar vẫn hiển thị đúng
    categories = dao.load_categories()
    return render_template("customer/cart.html", categories=categories)
@app.route("/admin")
def admin():
   return render_template("admin/admin.html")
@app.route("/create")
def create():
    return render_template("admin/create_voucher.html")


#NhuY Login, Register
@app.route("/login", methods=['get', 'post'])
def user_login():
    if current_user.is_authenticated:
        if int(current_user.user_role) == 1:
            return redirect('/admin')
        return render_template('customer/customer.html')

    err_msg = None
    if request.method.__eq__('POST'):
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_user(role, username, password)

        if user:
            login_user(user)
            if int(user.user_role) == 1:
                return redirect('/admin')
            return redirect('/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng!"
            return render_template("login.html", err_msg=err_msg)
    return render_template("login.html")

@app.route("/register",  methods=['get', 'post'])
def register():
    err_msg = None

    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get('email')

        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        # import pdb #kiểm tra lỗi
        # pdb.set_trace()

        if dao.check_username_exists(username):
            err_msg = "Tên đăng nhập này đã tồn tại! Vui lòng chọn tên khác."
        elif not re.match(password_pattern, password):
            err_msg = ("Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.")
        elif not password.__eq__(confirm):
            err_msg = "Mật khẩu không khớp!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            err_msg = "Định dạng email không hợp lệ!"
        else:
            name = request.form.get("name")
            username = request.form.get("username")
            avatar = request.files.get("avatar")
            path_file = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                path_file = res["secure_url"]
            try:
                dao.add_user(name, username, password, email, avatar=path_file)
                return redirect('/login')
            except:
                db.session.rollback()
                err_msg = "Hệ thống đang có lỗi! Vui lòng quay lại sau!"
    return render_template("register.html", err_msg=err_msg)

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(int(user_id))

@app.route('/logout')
def user_logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
