from discounts.test.conftest import test_client, mock_admin

VALID_DATA = {
    "MaGG": "SALE10",
    "GiaTri": "20000",
    "SoLuong": "10",
    "LoaiGG": "tien",
    "Hinhthuc": "Khuyến mãi",
    "NgayBD": "2026-05-15T10:00",
    "NgayKT": "2026-05-20T10:00"
}


# TC1: Thành công
def test_create_voucher_success(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mock_add = mocker.patch("discounts.index.add_voucher", return_value=True)

    res = test_client.post("/create", data=VALID_DATA)

    assert res.status_code == 302
    assert res.location.endswith("/admin")
    mock_add.assert_called_once()


# TC2: Trùng mã
def test_create_voucher_duplicate(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=True)

    res = test_client.post("/create", data=VALID_DATA)

    assert res.status_code == 302
    assert "/create" in res.location


# TC3: Mã rỗng
def test_create_voucher_empty_code(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["MaGG"] = ""

    res = test_client.post("/create", data=data)

    assert "/create" in res.location


# TC4: Mã sai format
def test_create_voucher_invalid_code_format(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["MaGG"] = "SALE@10!"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC5: Mã có khoảng trắng
def test_create_voucher_code_with_space(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["MaGG"] = "SALE 10"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC6: Ngày kết thúc <= ngày bắt đầu
def test_create_voucher_invalid_date_order(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["NgayBD"] = "2026-05-20T10:00"
    data["NgayKT"] = "2026-05-15T10:00"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC7: Ngày trong quá khứ
def test_create_voucher_past_date(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["NgayBD"] = "2020-01-01T10:00"
    data["NgayKT"] = "2020-01-02T10:00"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC8: Giá trị âm
def test_create_voucher_negative_discount(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["GiaTri"] = "-10"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC9: Số lượng âm
def test_create_voucher_negative_quantity(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["SoLuong"] = "-5"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC10: Số lượng = 0
def test_create_voucher_zero_quantity(test_client, mock_admin):
    data = VALID_DATA.copy()
    data["SoLuong"] = "0"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


# TC11: Thiếu toàn bộ field
def test_create_voucher_missing_all_fields(test_client, mock_admin):
    res = test_client.post("/create", data={})

    assert res.status_code == 302
    assert "/create" in res.location


# TC12: DB fail
def test_create_voucher_db_fail(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mock_add = mocker.patch("discounts.index.add_voucher", return_value=False)

    res = test_client.post("/create", data=VALID_DATA)

    assert res.status_code == 302
    assert "/create" in res.location
    mock_add.assert_called_once()


# TC13: Không phải admin
def test_create_voucher_not_admin(test_client):
    res = test_client.post("/create", data=VALID_DATA)

    assert res.status_code in (302, 403)


# TC14: Input sai → không gọi DB
def test_create_voucher_invalid_not_call_db(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id")
    mock_add = mocker.patch("discounts.index.add_voucher")

    res = test_client.post("/create", data={"MaGG": ""})

    assert res.status_code == 302
    assert not mock_add.called


# TC15: DB gọi đúng 1 lần
def test_create_voucher_call_db_once(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mock_add = mocker.patch("discounts.index.add_voucher", return_value=True)

    test_client.post("/create", data=VALID_DATA)

    mock_add.assert_called_once()


# TC16: Có flash message
def test_create_voucher_flash_message(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=True)

    with test_client as client:
        client.post("/create", data=VALID_DATA)

        with client.session_transaction() as session:
            assert "_flashes" in session


# TC17: min tiền hợp lệ
def test_create_voucher_min_money(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.index.add_voucher", return_value=True)

    data = VALID_DATA.copy()
    data["GiaTri"] = "10000"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302


# TC18: max tiền hợp lệ
def test_create_voucher_max_money(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.index.add_voucher", return_value=True)

    data = VALID_DATA.copy()
    data["GiaTri"] = "20000000"

    res = test_client.post("/create", data=data)

    assert res.status_code == 302