import pytest
from discounts import db, dao
from discounts.models import User
from werkzeug.security import generate_password_hash

# login khi chưa đăng nhập
def test_get_not_login(test_client):
    response = test_client.get('/login')
    assert response.status_code == 200


# 2. GET /login khi đã đăng nhập Admin -> Redirect /admin
def test_get_login_authenticated_admin_redirects_admin(test_client, test_app):
    with test_app.app_context():
        u = User(name="Ad", username="ad1", password=generate_password_hash("123"), user_role=1, type='admin')
        db.session.add(u)
        db.session.commit()
        with test_client.session_transaction() as sess:
            sess['_user_id'] = str(u.id)
        response = test_client.get('/login')
    assert response.status_code == 302
    assert '/admin' in response.location


# 3. GET /login khi đã đăng nhập Khách -> Redirect /
def test_get_login_authenticated_customer_redirects_home(test_client, test_app):
    with test_app.app_context():
        u = User(name="Kh", username="kh1", password=generate_password_hash("123"), user_role=0, type='khachhang')
        db.session.add(u)
        db.session.commit()
        with test_client.session_transaction() as sess:
            sess['_user_id'] = str(u.id)
        response = test_client.get('/login')
    assert response.status_code == 302
    assert response.location.endswith('/')


# 4. POST Login Admin thành công
def test_post_login_admin_success(test_client, test_app):
    with test_app.app_context():
        u = User(name="Admin", username="admin", password=generate_password_hash("Admin@123"), user_role=1,
                 type='admin')
        db.session.add(u)
        db.session.commit()
    response = test_client.post('/login', data={'role': '1', 'username': 'admin', 'password': 'Admin@123'})
    assert response.status_code == 302
    assert '/admin' in response.location


# 5. POST Login Khách thành công
def test_post_login_customer_success(test_client, test_app):
    with test_app.app_context():
        dao.add_user(name="User", username="user1", password="Pass@123", email="u1@gmail.com")
    response = test_client.post('/login', data={'role': '0', 'username': 'user1', 'password': 'Pass@123'})
    assert response.status_code == 302


# 6. POST Login sai mật khẩu
def test_post_login_wrong_password(test_client, test_app):
    with test_app.app_context():
        dao.add_user(name="User", username="user1", password="CorrectPass", email="u1@gmail.com")
    response = test_client.post('/login', data={'role': '0', 'username': 'user1', 'password': 'WrongPass'})
    assert "Sai tài khoản hoặc mật khẩu" in response.data.decode('utf-8')


# 7. POST Login sai username
def test_post_login_wrong_username(test_client):
    response = test_client.post('/login', data={'role': '0', 'username': 'no_exist', 'password': '123'})
    assert "Sai tài khoản hoặc mật khẩu" in response.data.decode('utf-8')


# 8. POST Login để trống trường dữ liệu
def test_post_login_empty_fields(test_client):
    response = test_client.post('/login', data={'role': '0', 'username': '', 'password': ''})
    assert "Sai tài khoản hoặc mật khẩu" in response.data.decode('utf-8')
