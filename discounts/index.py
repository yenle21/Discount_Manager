from flask import Flask, render_template, request
import json

from discounts import dao, app
from discounts.dao import load_products, load_categories

# Đọc dữ liệu từ JSON
@app.route("/")
def customer():
    cate_id = request.args.get("cate_id", type=int)  # lấy từ URL
    products = dao.load_products(cate_id=cate_id)

    categories = dao.load_categories()

    return render_template(
        "customer/customer.html",
        products=products,
        categories=categories,
        cate_id=cate_id,
    )
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
