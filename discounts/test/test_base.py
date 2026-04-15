import pytest
from flask import Flask
from flask_login import LoginManager
from discounts import db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.secret_key = '^#@$*Juifdyfuhsfai#@&#^*'
    app.config['CART_KEY'] = 'cart'

    db.init_app(app)

    login_manager.init_app(app)

    from discounts.index import register_routes
    register_routes(app)

    return app


@pytest.fixture
def test_app():
    app = create_app()

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()



@pytest.fixture
def test_client(test_app):
    return test_app.test_client()



@pytest.fixture
def test_session(test_app):
    with test_app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(autouse=True)
def mock_admin(monkeypatch):
    # bypass admin_required
    monkeypatch.setattr("discounts.index.admin_required", lambda f: f)

    # fake current_user
    class FakeUser:
        id = 1

    monkeypatch.setattr("flask_login.utils._get_user", lambda: FakeUser())