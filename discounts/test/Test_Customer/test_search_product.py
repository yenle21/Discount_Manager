
from discounts.dao import load_products


def test_all(sample_product):
    actual = load_products()
    assert len(actual) == len(sample_product)

def test_kw(sample_product):
    actual = load_products(kw='Mi')
    assert len(actual) == 2
    assert all('Mi' in p.name for p in actual)

def test_cateId(sample_product):
    actual = load_products(cate_id='1')
    assert len(actual) == 2
    assert all(p.category_id == 1 for p in actual)

def test_cateId_kw(sample_product):
    actual = load_products(cate_id='1', kw='Sua')
    assert len(actual) == 2
    assert all(p.category_id == 1 for p in actual)
    assert all('Sua' in p.name for p in actual)
    assert actual[0].name == 'Sua TH'

def test_page(sample_product,test_app):
    actual = load_products(page=1)

    assert len(actual) == test_app.config['PAGE_SIZE']
    assert actual[0].name == 'Sua TH'
    assert actual[1].name == 'Mi goi Hao Hao'

def test_page2(sample_product,test_app):
    actual = load_products(page=2)

    assert len(actual) == test_app.config['PAGE_SIZE']
    assert actual[0].name == 'Sua ong Tho'
    assert actual[1].name == 'Mi Indome'