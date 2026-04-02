from flask import Flask, render_template
from flask_login import LoginManager, current_user
from discounts import app, login
import json

# Đọc dữ liệu từ JSON
def load_products():
    with open("data/sanpham.json", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home():
    products = load_products()
    # return render_template("login.html", products=products)

    return render_template("register.html", products=products)

    # return render_template("customer.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
