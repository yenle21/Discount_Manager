import pytest
from unittest.mock import patch, MagicMock

# Test đăng ký thành công
@patch("cloudinary.uploader.upload")
def test_register_success(mock_upload, test_client, test_app):
    # Giả lập upload ảnh thành công
    mock_upload.return_value = {'secure_url': 'https://res.cloudinary.com/demo.jpg'}

    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'Abc@1234',
        'confirm': 'Abc@1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/login'

    # Kiểm tra database
    with test_app.app_context():
        from discounts.models import User
        user_db = User.query.filter_by(username='khach').first()

        assert user_db is not None
        assert user_db.email == 'abc@gmail.com'
        assert user_db.name == 'Nguyễn Khách'

# Test họ tên để trống
def test_register_empty_name(test_client):
    response = test_client.post('/register', data={
        'name': '',
        'username': 'khach',
        'password': 'Abc@1234',
        'confirm': 'Abc@1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)
    assert 'Họ tên không được để trống!' in response.data.decode('utf-8')

# Test tên tài khoản để trống
def test_register_empty_username(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': '',
        'password': 'Abc@1234',
        'confirm': 'Abc@1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Tên tài khoản không được để trống!' in response.data.decode('utf-8')

# Test tên tài khoản đã tồn tại
def test_register_username_exist(test_client, sample_users):
    user_exist = sample_users['user_customer']

    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach', # đã tồn tại
        'password': 'Abc@1234',
        'confirm': 'Abc@1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Tên đăng nhập này đã tồn tại! Vui lòng chọn tên khác.' in response.data.decode('utf-8')

# Test mật khẩu ít hơn 8 ký tự
def test_register_password_less_than_8(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'Abc@123',
        'confirm': 'Abc@123',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.' in response.data.decode('utf-8')

# Test mật khẩu không có chữ hoa
def test_register_password_no_uppercase(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'abc@1234',
        'confirm': 'abc@1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.' in response.data.decode('utf-8')

# Test mật khẩu không có chữ thường
def test_register_password_no_lowercase(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'ABC@1234',
        'confirm': 'ABC@1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.' in response.data.decode('utf-8')

# Test mật khẩu không có số
def test_register_password_no_number(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'ABC@defg',
        'confirm': 'ABC@defg',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.' in response.data.decode('utf-8')

# Test mật khẩu không có ký tự đặc biệt
def test_register_password_no_special_char(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'Abcd1234',
        'confirm': 'Abcd1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.' in response.data.decode('utf-8')

# Test mật khẩu xác nhận không khớp
def test_register_password_not_match(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'Abc@1234',
        'confirm': 'Abc1234',
        'email': 'abc@gmail.com'
    }, follow_redirects=True)

    assert 'Mật khẩu không khớp!' in response.data.decode('utf-8')

# Test định dạng email không hợp lệ
def test_register_invalid_email(test_client):
    response = test_client.post('/register', data={
        'name': 'Nguyễn Khách',
        'username': 'khach',
        'password': 'Abc@1234',
        'confirm': 'Abc@1234',
        'email': 'abcgmail.com'
    }, follow_redirects=True)

    assert 'Định dạng email không hợp lệ!' in response.data.decode('utf-8')