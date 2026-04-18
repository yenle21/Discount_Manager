# la admin dang nhap thanh cong
def test_create_route_login(mock_admin, test_client, mocker):
    mock_update = mocker.patch(
        "discounts.dao.load_categories",
        return_value=["cate1"]
    )

    res = test_client.get("/create")

    assert res.status_code == 200
    mock_update.assert_called()
# chua dang nhap
def test_create_route_no_login(test_client, mocker):
    # Giả lập user chưa đăng nhập
    mock_user = mocker.patch("discounts.decorators.current_user")
    mock_user.is_authenticated = False

    res = test_client.get("/create", follow_redirects=False)

    assert res.status_code == 302
    assert "/login" in res.location

# test ko phai la admin
def test_create_route_forbidden(test_client, mocker):
    mock_user = mocker.patch("discounts.decorators.current_user")
    mock_user.is_authenticated = True
    mock_user.user_role = 0

    res = test_client.get("/create", follow_redirects=False)

    assert res.status_code == 302
    assert "/" in res.location
