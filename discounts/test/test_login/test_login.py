import pytest
from discounts import db, dao
from discounts.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from unittest.mock import patch
from discounts.index import otp_storage

# Test vào được trang login
def test_get_login(test_client):
    response = test_client.get('/login') # gửi yêu cầu đến trang login
    assert response.status_code == 200 # thành công

# Test vào đúng trang /admin khi đăng nhập bằng tài khoản admin
def test_get_admin_login(test_client, sample_users):
    user_admin = sample_users['user_admin']

    # Giả lập trạng thái đã đăng nhập
    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user_admin.id)
    response = test_client.get('/login')

    assert response.status_code == 302 # Found/Redirect (Điều hướng)
    assert '/admin' in response.location # kiểm tra url có chứa /admin không


# Test vào đúng trang chủ khi đăng nhập bằng tài khoản customer
def test_get_customer_login(test_client, sample_users):
    user_customer = sample_users['user_customer']

    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user_customer.id)
    response = test_client.get('/login')

    assert response.status_code == 302
    assert response.location.endswith('/') # kiểm tra url có kết thúc bằng dấu / không


# Test login admin thành công
def test_post_admin_login(test_client, sample_users):
    user_admin = sample_users['user_admin']

    response = test_client.post('/login', data={'role': '1', 'username': 'admin', 'password': '123'})

    assert response.status_code == 302
    assert '/admin' in response.location

# Test login customer thành công
def test_post_customer_login(test_client, sample_users):
    user_customer = sample_users['user_customer']

    response = test_client.post('/login', data={'role': '0', 'username': 'khach', 'password': '123'})

    assert response.status_code == 302
    assert response.location.endswith('/')

# Test login sai mật khẩu
def test_login_wrong_password(test_client, sample_users):
    user_customer = sample_users['user_customer']

    response = test_client.post('/login', data={'role': '0', 'username': 'khach', 'password': 'abc'})
    assert "Sai tài khoản hoặc mật khẩu!" in response.data.decode('utf-8') # nội dung server trả về cho trình duyệt

# Test login sai username
def test_login_wrong_username(test_client, sample_users):
    user_customer = sample_users['user_customer']

    response = test_client.post('/login', data={'role': '0', 'username': 'sai', 'password': '123'})
    assert "Sai tài khoản hoặc mật khẩu!" in response.data.decode('utf-8')

# Test customer login sai role
def test_customer_login_wrong_role(test_client, sample_users):
    user_customer = sample_users["user_customer"]

    response = test_client.post('/login', data={'role': '1', 'username': 'khach', 'password': '123'})
    assert "Sai tài khoản hoặc mật khẩu!" in response.data.decode('utf-8')

# Test admin login sai role
def test_admin_login_wrong_role(test_client, sample_users):
    user_admin = sample_users["user_admin"]

    response = test_client.post('/login', data={'role': '0', 'username': 'admin', 'password': '123'})
    assert "Sai tài khoản hoặc mật khẩu!" in response.data.decode('utf-8')

# Test login không điền thông tin
def test_login_empty_data(test_client):
    response = test_client.post('/login', data={'role': '0', 'username': '', 'password': ''})
    assert "Sai tài khoản hoặc mật khẩu!" in response.data.decode('utf-8')

# Test gửi OTP khi quên mật khẩu
def test_send_otp(test_client, sample_users):
    user_customer = sample_users['user_customer']

    # không gửi mail thật và tránh lỗi mail
    with patch('flask_mail.Mail.send') as mock_mail:
        response = test_client.post('/api/send-otp', json={
            'username': user_customer.username,
            'email': user_customer.email
        })

        data = response.get_json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['message'] == "OTP đã được gửi! Bạn kiểm tra hòm thư nhé."

# Test gửi OTP thất bại (Sai email)
def test_send_otp_wrong_email(test_client, sample_users):
    user_customer = sample_users['user_customer']

    response = test_client.post('/api/send-otp', json={
        'username': user_customer.username,
        'email': 'abc@gmail.com'
    })

    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is False
    assert data['message'] == "Thông tin không khớp! Kiểm tra lại Username hoặc Email"

# Test gửi OTP thất bại (Sai username)
def test_send_otp_wrong_username(test_client, sample_users):
    user_customer = sample_users['user_customer']

    response = test_client.post('/api/send-otp', json={
        'username': 'abc',
        'email': user_customer.email
    })

    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is False
    assert data['message'] == "Thông tin không khớp! Kiểm tra lại Username hoặc Email"

# Test xác thực OTP thành công và đổi mật khẩu
def test_verify_reset_and_update_db_success(test_client, test_app, sample_users):
    user_customer = sample_users['user_customer']
    otp_storage[user_customer.email] = '123456'

    # Gọi API xác thực và đổi mật khẩu
    response = test_client.post('/api/verify-reset', json={
        'email': user_customer.email,
        'otp': '123456',
        'new_password': 'Abc@1234'
    })

    # Kiểm tra phản hồi từ API
    data = response.get_json()
    assert response.status_code == 200
    assert data['success'] is True
    assert data['message'] == 'Đổi mật khẩu thành công! Hãy đăng nhập lại.'

    # Kiểm tra trong Database
    with test_app.app_context():
        update_user = User.query.filter_by(email=user_customer.email).first()
        # Xác nhận mật khẩu mới đã được lưu và hash đúng
        assert check_password_hash(update_user.password, 'Abc@1234') is True
        # Kiểm tra OTP phải được xóa sau khi dùng
        assert user_customer.email not in otp_storage

# Test xác thực thất bại (Sai mã OTP)
def test_verify_wrong_otp(test_client, sample_users):
    user_customer = sample_users["user_customer"]
    otp_storage[user_customer.email] = '123456'

    response = test_client.post('/api/verify-reset', json={
        'email': user_customer.email,
        'otp': '999999',  # OTP sai
        'new_password': 'Abc@1234'
    })

    data = response.get_json()

    assert data['success'] is False
    assert data['message'] == "Mã OTP không đúng hoặc đã hết hạn!"

# Test xác thực thất bại (OTP không tồn tại/Hết hạn)
def test_verify_otp_timeout(test_client, sample_users):
    user_customer = sample_users['user_customer']
    # Giả lập OTP đã bị xóa do hết hạn hoặc người dùng chưa yêu cầu gửi mã xác thực
    if user_customer.email in otp_storage:
        del otp_storage[user_customer.email]

    response = test_client.post('/api/verify-reset', json={
        'email': user_customer.email,
        'otp': '123456',
        'new_password': 'Abc@1234'
    })

    data = response.get_json()

    assert data['success'] is False
    assert data['message'] == "Mã OTP không đúng hoặc đã hết hạn!"

# Test customer logout
def test_customer_logout(test_client, sample_users):
    user_customer = sample_users["user_customer"]

    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user_customer.id)
    response = test_client.get('/logout', follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/')

    with test_client.session_transaction() as sess:
        assert '_user_id' not in sess

# Test admin logout
def test_admin_logout(test_client, sample_users):
    user_admin = sample_users["user_admin"]

    with test_client.session_transaction() as sess:
        sess['_user_id'] = str(user_admin.id)
    response = test_client.get('/logout', follow_redirects=False)

    assert response.status_code == 302
    assert response.location.endswith('/')

    with test_client.session_transaction() as sess:
        assert '_user_id' not in sess