from datetime import datetime, timedelta
from discounts.dao import update_voucher

def test_edit_voucher_view(test_client, sample_voucher):
    response = test_client.get(f'/edit/{sample_voucher.MaGG}')
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    assert sample_voucher.MaGG in html_content
    assert "Chỉnh sửa Voucher" in html_content

def test_edit_voucher_success(test_client,mocker,sample_voucher,mock_admin):
    mock_add =  mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "10",
        "SoLuong": "100",
        "NgayBD": "2026-04-16T08:00",
        "NgayKT": "2026-04-30T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data,follow_redirects=True)

    assert res.status_code == 200
    assert f"Cập nhật mã {sample_voucher.MaGG} thành công!".encode('utf-8') in res.data
    mock_add.assert_called_once()

def test_edit_exception(test_client, sample_voucher, mocker):
    # ép văng lỗi ngay khi được gọi
    mocker.patch("discounts.dao.update_voucher", side_effect=Exception("Database Connection Error"))
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "10",
        "SoLuong": "100",
        "NgayBD": "2026-04-16T08:00",
        "NgayKT": "2026-04-30T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }

    # 2. Thả mồi: Thực hiện post dữ liệu
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)
    assert res.status_code == 200
    assert "Database Connection Error".encode('utf-8') in res.data

def test_start_day_none(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "10",
        "SoLuong": "100",
        "NgayBD": "",
        "NgayKT": "2026-04-30T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_end_day_none(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "10",
        "SoLuong": "100",
        "NgayBD": "2026-04-30T23:59",
        "NgayKT": "",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_ngaybd_gt_ngaykt(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "10",
        "SoLuong": "100",
        "NgayBD": "2026-04-30T23:59",
        "NgayKT": "2026-04-01T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Ngày kết thúc phải lớn hơn ngày bắt đầu!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_ngkt_lt_now(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    now = datetime.now()
    ngay_bd = (now - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M")
    ngay_kt = (now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "10",
        "SoLuong": "100",
        "NgayBD": ngay_bd,
        "NgayKT": ngay_kt,
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Ngày kết thúc không được ở quá khứ!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_gia_tri_none(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "",
        "SoLuong": "100",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Vui lòng nhập đầy đủ thông tin!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_so_luong_none(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "1",
        "SoLuong": "",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Vui lòng nhập đầy đủ thông tin!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_loaigg_none(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "",
        "GiaTri": "1",
        "SoLuong": "1",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Vui lòng nhập đầy đủ thông tin!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_hinh_thuc_gg_invalid(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "test",
        "LoaiGG": "test",
        "GiaTri": "1",
        "SoLuong": "1",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Hình thức giảm giá không hợp lệ!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_phan_tram_is_0(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "0",
        "SoLuong": "1",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Phần trăm giảm giá phải từ 1 đến 50!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_phan_tram_gt_50(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "phantram",
        "GiaTri": "51",
        "SoLuong": "1",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Phần trăm giảm giá phải từ 1 đến 50!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_tien_giam_lt_10000(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "5000",
        "SoLuong": "1",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_tien_giam_lt_20000000(test_client, sample_voucher,mocker):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "21000000",
        "SoLuong": "1",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_so_luong_phat_hanh_lt_0(test_client, sample_voucher,mocker,mock_admin):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "50000",
        "SoLuong": "0",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Số lượng phát hành không hợp lệ".encode('utf-8') in res.data

    mock_add.assert_not_called()
def test_so_luong_phat_hanh_gt_1000(test_client, sample_voucher,mocker,mock_admin):
    mock_add = mocker.patch("discounts.dao.update_voucher")
    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "50000",
        "SoLuong": "1001",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Số lượng phát hành không hợp lệ".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_add_voucher_data_type_error(test_client, mocker, mock_admin,sample_voucher):
    mock_add =mocker.patch("discounts.dao.update_voucher")

    form_data = {
        "Hinhthuc": "Khuyến mãi",
        "LoaiGG": "tien",
        "GiaTri": "abc",
        "SoLuong": "1001",
        "NgayBD": "2026-04-15T23:59",
        "NgayKT": "2026-04-16T23:59",
        "TrangThai": "active",
        "MoTa": "Mô tả đã cập nhật",
        "DieuKien": "50000",
        "DieuKienSP": "1"
    }
    res = test_client.post(f'/update/{sample_voucher.MaGG}', data=form_data, follow_redirects=True)

    assert res.status_code == 200
    assert "Định dạng dữ liệu số hoặc ngày tháng không đúng!".encode('utf-8') in res.data

    mock_add.assert_not_called()

def test_update_voucher_exception(test_client, mocker):
    mock_query = mocker.patch("discounts.dao.get_voucher_by_maGG")
    mock_commit = mocker.patch("discounts.dao.db.session.commit", side_effect=Exception("Lỗi update voucher giả lập"))
    fake_data = {"GiaTri": 50000, "SoLuong": 10, "Hinhthuc": "test"}
    result = update_voucher("Mã_GG_TEST", fake_data)

    assert result is False  # Hàm phải trả về False vì đã rớt vào except
    mock_commit.assert_called_once()  # Đảm bảo đã chạy tới dòng commit và gây ra lỗi


