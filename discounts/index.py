from flask import Flask, render_template, request
import json

from discounts import dao
from discounts.dao import load_products, load_categories

app = Flask(__name__)

# Đọc dữ liệu từ JSON
@app.route("/")
def customer():
    cate_id = request.args.get("cate_id", type=int)  # lấy từ URL
    products = dao.load_products(cate_id=cate_id)

    categories = dao.load_categories()

    return render_template(
        "customer.html",
        products=products,
        categories=categories,
        cate_id=cate_id,
    )
if __name__ == "__main__":
    app.run(debug=True)
