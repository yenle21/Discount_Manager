from unittest.mock import patch
from discounts.models import Voucher
from discounts.models import UserRole

from discounts.test.conftest import test_client,test_app

from discounts.test.conftest import test_client,test_app, mock_admin


def test_add_voucher_success(test_client, monkeypatch):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)
    monkeypatch.setattr("discounts.dao.add_voucher", lambda x: True)

    data = {
        "MaGG": "SALE10",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302

def test_add_voucher_duplicate(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: True)

    data = {"MaGG": "SALE10"}

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_empty_code(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_code_with_space(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE 10",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_special_char_code(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE@10!",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


def test_add_voucher_invalid_date(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE10",
        "NgayBD": "2026-04-20T10:00",
        "NgayKT": "2026-04-15T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_past_date(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE10",
        "NgayBD": "2020-01-01T10:00",
        "NgayKT": "2020-01-02T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_negative_discount(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE10",
        "GiaTri": "-10",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_negative_quantity(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE10",
        "SoLuong": "-5",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_negative_condition(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)

    data = {
        "MaGG": "SALE10",
        "DieuKien": "-100",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location

def test_add_voucher_db_fail(test_client, monkeypatch,mock_admin):
    monkeypatch.setattr("discounts.dao.get_voucher_by_id", lambda x: None)
    monkeypatch.setattr("discounts.index.add_voucher", lambda x: False)

    data = {
        "MaGG": "SALE10",
        "NgayBD": "2026-04-15T10:00",
        "NgayKT": "2026-04-20T10:00"
    }

    res = test_client.post("/add", data=data)

    assert res.status_code == 302
    assert "/create" in res.location


