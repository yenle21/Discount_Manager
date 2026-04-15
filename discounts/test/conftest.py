import pytest
from flask import Flask

from discounts import db
from discounts.models import Product


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config['PAGE_SIZE'] = 2
    app.secret_key =  '^#@$*Juifdyfuhsfai#@&#^*'
    db.init_app(app)

    from discounts.index import register_routes
    register_routes(app)

    return app

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_session(test_app):
    yield  db.session
    db.session.rollback()


@pytest.fixture()
def test_cloudinary(monkeypatch):
    def fake_upload(file):
        return{'secure_url':'https://fake-image.png'}

    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)

@pytest.fixture
def sample_product(test_session):
    p1 = Product(name='Sua TH', price=30, category_id=1)
    p2 = Product(name='Mi goi Hao Hao', price=20, category_id=2)
    p3 = Product(name='Sua ong Tho', price=35, category_id=1)
    p4 = Product(name='Mi Indome', price=35, category_id=2)

    test_session.add_all([p1, p2, p3, p4])
    test_session.commit()

    yield [p1, p2, p3, p4]
