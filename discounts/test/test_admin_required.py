# 1. Admin truy cập thành công
def test_admin_required_success(test_client, mocker):
    # Patch đúng nơi sử dụng
    mock_user = mocker.patch("discounts.decorators.current_user")

    mock_user.is_authenticated = True
    mock_user.user_role = 1  # ADMIN
    mock_user.name = "Admin Bao Yen"

    res = test_client.get('/admin', follow_redirects=True)

    assert res.status_code == 200
    assert "Bạn không có quyền truy cập vào trang này!".encode('utf-8') not in res.data


# 2. User thường (không phải admin)
def test_admin_required_forbidden(test_client, mocker):
    mock_user = mocker.Mock()
    mock_user.is_authenticated = True
    mock_user.user_role = 0

    mocker.patch("discounts.decorators.current_user", mock_user)

    res = test_client.get('/admin', follow_redirects=False)

    assert res.status_code == 302
    assert res.headers['Location'] == '/login'

# 3. Chưa đăng nhập
def test_admin_required_unauthenticated(test_client, mocker):
    mock_user = mocker.patch("discounts.decorators.current_user")

    mock_user.is_authenticated = False
    mock_user.user_role = None

    res = test_client.get('/admin', follow_redirects=True)

    assert res.status_code == 200
