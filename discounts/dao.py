from werkzeug.security import generate_password_hash, check_password_hash
import email
from discounts.models import User, KhachHang, Category, Product

#from models import Category, Product
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


#NhuY
def get_user_by_id(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

def add_user(name, username, password, avatar=None, email=None, sdt=None):
    password = generate_password_hash(password.strip())

    u = KhachHang(name=name,
                  username=username.strip(),
                  password=password,
                  avatar=avatar,
                  email=email,
                  sdt=sdt,
                  user_role=0)

    db.session.add(u)
    db.session.commit()
    return u

def check_username_exists(username):
    return User.query.filter(User.username == username.strip()).first() is not None

def auth_user(role, username, password):
    user = User.query.filter(User.user_role == int(role), User.username == username.strip()).first()

    if user and check_password_hash(user.password, password.strip()):
        return user

    return None