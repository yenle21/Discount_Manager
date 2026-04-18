
from discounts.dao import load_products, count_product


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

def test_search_no_result(sample_product):
    # Tìm kiếm từ khóa không tồn tại
    actual = load_products(kw='Thit ga')
    assert len(actual) == 0

def test_cate_no_result(sample_product):
    # Lọc danh mục không tồn tại (giả sử chỉ có id 1 và 2)
    actual = load_products(cate_id='999')
    assert len(actual) == 0

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

def test_count_product_valid(sample_product,mocker):
    mock_query = mocker.patch('discounts.dao.Product.query')
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 5
    result = count_product(cate_id=1, kw="iPhone")

    assert result == 5
    # Đảm bảo hàm filter được gọi 2 lần (1 cho cate_id, 1 cho kw)
    assert mock_query.filter.call_count == 2
    mock_query.count.assert_called_once()