from flask import Flask, render_template
import json

app = Flask(__name__)

# Đọc dữ liệu từ JSON
def load_products():
    with open("data/sanpham.json", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home():
    products = load_products()
    return render_template("customer.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
