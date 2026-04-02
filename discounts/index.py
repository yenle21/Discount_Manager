<<<<<<< HEAD
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from discounts import app, login
import json

=======
from flask import Flask, render_template, request
import json

from discounts import dao, app
from discounts.dao import load_products, load_categories

>>>>>>> 893d5ed7924071a573d8a43ef4dd187172844816
# Đọc dữ liệu từ JSON
@app.route("/")
<<<<<<< HEAD
def home():
    products = load_products()
    # return render_template("login.html", products=products)

    return render_template("register.html", products=products)

    # return render_template("customer.html", products=products)
=======
def index():
    # 1. Lấy cate_id từ URL (ví dụ: /?category_id=1)
    cate_id = request.args.get('category_id')
>>>>>>> 893d5ed7924071a573d8a43ef4dd187172844816

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
if __name__ == "__main__":
    app.run(debug=True)
