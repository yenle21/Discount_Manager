import hashlib

from werkzeug.security import generate_password_hash, check_password_hash
from discounts.models import User, KhachHang, Category, Product, Voucher
from discounts import db, app

# --- PRODUCT LOGIC ---
def load_categories():
    return Category.query.all()

def load_products(cate_id=None, kw=None, page=None):
    query = Product.query
    if cate_id and cate_id not in ['None', '0']:
        query = query.filter(Product.category_id == int(cate_id))
    if kw:
        query = query.filter(Product.name.contains(kw))
    if page:
        size = app.config.get("PAGE_SIZE", 8)
        query = query.slice((int(page) - 1) * size, int(page) * size)
    return query.all()

def count_product(cate_id=None, kw=None):
    query = Product.query
    if cate_id: query = query.filter(Product.category_id == cate_id)
    if kw: query = query.filter(Product.name.contains(kw))
    return query.count()

def get_product_by_id(product_id):
    return db.session.get(Product, product_id)

# --- USER & AUTH LOGIC (NHU Y) ---
def get_user_by_id(user_id):
    try:
        return db.session.get(User, int(user_id))
    except:
        return None

def add_user(name, username, password, email=None, sdt=None, avatar=None):
    u = KhachHang(name=name, username=username.strip(),
                  password=generate_password_hash(password.strip()),
                  avatar=avatar, email=email, sdt=sdt, user_role=0)
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

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_user_by_email(email):
    """Tìm user bằng username (email)"""
    return User.query.filter_by(username=email).first()


def update_password(email, new_password):
    """Cập nhật mật khẩu mới (Sử dụng Werkzeug Hash để đồng bộ)"""
    try:
        # Tìm user theo email (Lưu ý: Nếu username của Yến chính là email thì để nguyên)
        user = User.query.filter_by(email=email).first()

        if user:
            # Dùng generate_password_hash để đồng bộ với hàm add_user và auth_user
            user.password = generate_password_hash(new_password.strip())
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"Lỗi đổi mật khẩu: {e}")
        db.session.rollback()
        return False

#QNHU
def get_all_vouchers():
    return Voucher.query.all()


def get_voucher_by_id(maGG):
    return db.session.get(Voucher, maGG)


def add_voucher(data):
    try:
        voucher = Voucher(**data)
        db.session.add(voucher)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print("DAO ERROR:", e)
        return False
####QNHU