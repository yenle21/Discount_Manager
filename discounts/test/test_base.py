import pytest
from flask import Flask
from discounts import db
from discounts.models import Product, Category   # thêm dòng này


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.secret_key = '^#@$*Juifdyfuhsfai#@&#^*'
    app.config['CART_KEY'] = 'cart'
    db.init_app(app)

    from discounts.index import register_routes
    register_routes(app)

    return app


# 🔹 App fixture
@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# 🔹 Client
@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


# 🔹 DB session
@pytest.fixture
def test_session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()


# 🔹 Sample data
# @pytest.fixture
# def sample_product(test_session):
#     cate1 = Category(id=1, name="Sữa")
#     cate2 = Category(id=2, name="Kem")
#
#     p1 = Product(id=1, name="Sữa Vinamilk", price=10, category_id=1)
#     p2 = Product(id=2, name="Sữa Nuti", price=12, category_id=1)
#     p3 = Product(id=3, name="Kem Bắp", price=8, category_id=2)
#
#     test_session.add_all([cate1, cate2, p1, p2, p3])
#     test_session.commit()
#
#     yield [p1, p2, p3]