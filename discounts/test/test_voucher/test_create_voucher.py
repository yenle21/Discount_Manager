from discounts.test.conftest import test_client, mock_admin

def test_add_voucher_success(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mock_add = mocker.patch("discounts.index.add_voucher", return_value=True)

    data = {
        "MaGG": "SALE10",
        "GiaTri": "20000",
        "SoLuong": "10",
        "LoaiGG": "tien",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert res.location.endswith("/admin")
    mock_add.assert_called_once()


def test_add_voucher_duplicate(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=True)

    res = test_client.post("/add", data={"MaGG": "SALE10"})

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_empty_code(test_client, mock_admin):
    res = test_client.post("/add", data={"MaGG": ""})

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_invalid_code_format(test_client, mock_admin):
    data = {"MaGG": "SALE@10!"}

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_code_with_space(test_client, mock_admin):
    data = {"MaGG": "SALE 10"}

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_invalid_date_order(test_client, mock_admin):
    data = {
        "MaGG": "SALE10",
        "NgayBD": "2026-05-20T10:00",
        "NgayKT": "2026-05-15T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_past_date(test_client, mock_admin):
    data = {
        "MaGG": "SALE10",
        "NgayBD": "2020-01-01T10:00",
        "NgayKT": "2020-01-02T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_negative_discount(test_client, mock_admin):
    data = {
        "MaGG": "SALE10",
        "GiaTri": "-10"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_negative_quantity(test_client, mock_admin):
    data = {
        "MaGG": "SALE10",
        "SoLuong": "-5"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_zero_quantity(test_client, mock_admin):
    data = {
        "MaGG": "SALE10",
        "SoLuong": "0"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302


def test_add_voucher_missing_all_fields(test_client, mock_admin):
    res = test_client.post("/add", data={})

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_missing_date(test_client, mock_admin):
    res = test_client.post("/add", data={"MaGG": "SALE10"})

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_db_fail(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mock_add = mocker.patch("discounts.index.add_voucher", return_value=False)

    data = {
        "MaGG": "SALE10",
        "GiaTri": "20000",
        "SoLuong": "10",
        "LoaiGG": "tien",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location
    mock_add.assert_called_once()

def test_add_voucher_not_admin(test_client):
    data = {
        "MaGG": "SALE10",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code in (302, 403)


def test_add_voucher_invalid_not_call_db(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id")
    mock_add = mocker.patch("discounts.index.add_voucher")

    res = test_client.post("/add", data={"MaGG": ""})

    assert res.status_code == 302
    assert not mock_add.called


def test_add_voucher_call_db_once(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mock_add = mocker.patch("discounts.index.add_voucher", return_value=True)

    data = {
        "MaGG": "SALE10",
        "GiaTri": "20000",
        "SoLuong": "10",
        "LoaiGG": "tien",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-05-15T10:00",
        "NgayKT": "2026-05-20T10:00"
    }

    test_client.post("/add", data=data)

    mock_add.assert_called_once()

def test_add_voucher_flash_message(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=True)

    with test_client as client:
        client.post("/add", data={"MaGG": "SALE10"})

        with client.session_transaction() as session:
            assert "_flashes" in session

def test_add_voucher_min_money(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.index.add_voucher", return_value=True)

    data = {
        "MaGG": "MIN10K",
        "GiaTri": "10000",
        "SoLuong": "10",
        "LoaiGG": "tien",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-06-01T10:00",
        "NgayKT": "2026-06-10T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302


def test_add_voucher_max_money(test_client, mock_admin, mocker):
    mocker.patch("discounts.index.get_voucher_by_id", return_value=None)
    mocker.patch("discounts.index.add_voucher", return_value=True)

    data = {
        "MaGG": "MAX20M",
        "GiaTri": "20000000",
        "SoLuong": "10",
        "LoaiGG": "tien",
        "Hinhthuc": "Khuyến mãi",
        "NgayBD": "2026-06-01T10:00",
        "NgayKT": "2026-06-10T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302

