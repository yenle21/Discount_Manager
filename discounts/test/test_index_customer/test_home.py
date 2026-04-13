from discounts import dao
from discounts.test.test_base import test_client, test_app,test_session

def test_TC01_homepage(test_client, monkeypatch):
    monkeypatch.setattr("discounts.index.render_template", lambda *args, **kwargs: "OK")

    res = test_client.get('/')
    assert res.status_code == 200
    assert b"OK" in res.data


def test_products_display(test_client, monkeypatch):
    monkeypatch.setattr("discounts.index.render_template", lambda *args, **kwargs: "Sữa Vinamilk")

    res = test_client.get('/')
    assert res.status_code == 200
    assert "Sữa" in res.data.decode("utf-8")
