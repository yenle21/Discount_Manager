import json


def load_categories():
    with open("data/category.json", encoding="utf-8") as f:
        return json.load(f)
def load_products(cate_id=None):
    with open("data/product.json", encoding="utf-8") as f:
        data = json.load(f)

        if cate_id:
            # Ép kiểu int(p["category_id"]) để chắc chắn so sánh đúng với cate_id từ URL
            return [p for p in data if int(p["category_id"]) == int(cate_id)]

        return data

