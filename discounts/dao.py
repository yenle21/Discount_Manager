from models import Category, Product
from discounts import db

def load_categories():
    """Lấy tất cả danh mục từ Database"""
    return Category.query.all()

def load_products(cate_id=None, kw=None):
    query = Product.query

    # Lọc theo danh mục nếu có truyền cate_id
    if cate_id:
        query = query.filter(Product.category_id == int(cate_id))

    # Lọc theo từ khóa tìm kiếm nếu có truyền kw
    if kw:
        query = query.filter(Product.name.contains(kw))

    return query.all()

def get_product_by_id(product_id):
    """Lấy chi tiết một sản phẩm theo ID"""
    return db.session.get(Product, product_id)
