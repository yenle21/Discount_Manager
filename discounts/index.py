import random
import re
import cloudinary
import cloudinary.uploader
import datetime
import math
import json
from flask import render_template, session, request, jsonify, redirect, url_for, flash, current_app
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message, Mail
from discounts.dao import load_products, load_categories, add_voucher, get_voucher_by_id
from discounts import app, db, login, dao, utils
from discounts.decorators import admin_required
from discounts.models import UserRole, Voucher, CTHD, DonHang, Product, Category,User
from datetime import datetime
mail = Mail()
otp_storage = {}

def register_routes(app):
    global mail
    mail.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'nhu.nt2508@gmail.com'  # <-- Email của bạn
    app.config['MAIL_PASSWORD'] = 'jtpq brbn wldf ywrl'  # <-- Mật khẩu ứng dụng của bạn
    app.config['MAIL_DEFAULT_SENDER'] = 'nhu.nt2508@gmail.com'

    mail = Mail(app)  # Khởi tạo mail server

    # --- 1. TRANG CHỦ ---
    @app.route("/")
    def index():
        page = request.args.get("page", 1, type=int)
        cate_id = request.args.get('category_id')
        kw = request.args.get('kw')

        categories = dao.load_categories()
        products = dao.load_products(kw=kw, cate_id=cate_id, page=page)

        total_products = dao.count_product(cate_id=cate_id, kw=kw)
        page_size = app.config.get("PAGE_SIZE", 8)
        total_pages = math.ceil(total_products / page_size)

        cart = session.get('cart', {})
        total_quantity = sum(item['quantity'] for item in cart.values())

        return render_template('customer/customer.html',
                               categories=categories,
                               products=products,
                               pages=total_pages,
                               current_page=page,
                               total_quantity=total_quantity)


    #---------------- TRANG ADMIN ------------------------
    # danh sách voucher
    @app.route('/admin')
    @admin_required
    def admin_voucher():
        trang_thai = request.args.get('trang_thai')
        hinh_thuc = request.args.get('hinh_thuc')
        kw = request.args.get('kw')
        vouchers = dao.get_all_vouchers()
        filtered = []
        hinh_thuc_list = set()

        for v in vouchers:
            now = datetime.now()

            v.DaSuDung = v.DaSuDung or 0
            v.SoLuong = v.SoLuong or 0

            het_han = v.NgayKT and now >= v.NgayKT
            da_dung_het = v.SoLuong > 0 and v.DaSuDung == v.SoLuong
            chua_dung = v.DaSuDung == 0

            v.can_delete = het_han or da_dung_het or chua_dung
            if v.Hinhthuc:
                hinh_thuc_list.add(v.Hinhthuc)
            now = datetime.now()

            if v.NgayKT and now > v.NgayKT:
                display_status = "expired"

            elif v.NgayBD and now < v.NgayBD:
                display_status = "pending"

            elif v.TrangThai == 'Inactive':
                display_status = "exprired"

            elif v.SoLuong and v.DaSuDung >= v.SoLuong:
                display_status = "exprired"

            else:
                display_status = "active"
            v.display_status = display_status

            # 3. Bộ lọc Search
            if kw and kw.lower() not in (v.MaGG or "").lower() and kw.lower() not in (v.MoTa or "").lower():
                continue
            # 4. Bộ lọc theo Trạng thái
            if trang_thai:
                if display_status.strip().lower() != trang_thai.strip().lower():
                    continue

            # 5. Bộ lọc theo Hình thức (Khuyến mãi/Vận chuyển)
            if hinh_thuc and str(v.Hinhthuc).strip().lower() != str(hinh_thuc).strip().lower():
                continue

            filtered.append(v)
        return render_template(
            'admin/admin.html',
            vouchers=filtered,
            hinh_thuc_list=list(hinh_thuc_list),
            hinh_thuc=hinh_thuc,
            trang_thai=trang_thai,
            kw=kw
        )


    @app.route("/create")
    @admin_required
    def create():
        categories = dao.load_categories()
        return render_template("admin/create_voucher.html", categories=categories)

    @app.route('/create', methods=['GET', 'POST'])
    @admin_required
    def add_voucher_route():
        try:
            if request.method == 'POST':
                MaGG = (request.form.get('MaGG') or "").strip()

                raw_gia_tri = request.form.get('GiaTri')
                raw_so_luong = request.form.get('SoLuong')
                raw_dieu_kien = request.form.get('DieuKien')
                ngay_bd_str = request.form.get('NgayBD')
                ngay_kt_str = request.form.get('NgayKT')
                hinhthuc_str = request.form.get('Hinhthuc')
                loaigg = request.form.get('LoaiGG')
                raw_dksp = request.form.get('DieuKienSP')

                dieu_kien_sp = int(raw_dksp) if raw_dksp and raw_dksp.strip() != "" else None

                # 🔥 VALIDATION

                if not MaGG:
                    flash("Vui lòng nhập Mã Voucher!", "danger")
                    return redirect('/create')

                if get_voucher_by_id(MaGG):
                    flash("Mã voucher đã tồn tại!", "danger")
                    return redirect('/create')

                if " " in MaGG or not re.match("^[A-Za-z0-9]+$", MaGG):
                    flash("Mã voucher không hợp lệ!", "danger")
                    return redirect('/create')

                if not ngay_bd_str or not ngay_kt_str:
                    flash("Vui lòng nhập đầy đủ ngày!", "danger")
                    return redirect('/create')

                if not hinhthuc_str or not loaigg:
                    flash("Thiếu thông tin!", "danger")
                    return redirect('/create')

                # Ép kiểu
                try:
                    gia_tri = float(raw_gia_tri)
                    so_luong = int(raw_so_luong)
                    dieu_kien = float(raw_dieu_kien or 0)

                    ngay_bd = datetime.strptime(ngay_bd_str, "%Y-%m-%dT%H:%M")
                    ngay_kt = datetime.strptime(ngay_kt_str, "%Y-%m-%dT%H:%M")
                except:
                    flash("Sai định dạng dữ liệu!", "danger")
                    return redirect('/create')

                # Business logic
                if ngay_kt <= ngay_bd:
                    flash("Ngày kết thúc phải lớn hơn ngày bắt đầu!", "danger")
                    return redirect('/create')

                if ngay_kt < datetime.now():
                    flash("Ngày kết thúc không hợp lệ!", "danger")
                    return redirect('/create')

                if so_luong <= 0 or so_luong > 1000:
                    flash("Số lượng không hợp lệ!", "danger")
                    return redirect('/create')
                if gia_tri <= 0:
                    flash("Giá trị giảm phải lớn hơn 0!", "danger")
                    return redirect('/create')
                if gia_tri > 20000000:
                    flash("Giá trị giảm phải nhỏ hơn 20.000.000!", "danger")
                    return redirect('/create')

                # Lưu DB
                data = {
                    "MaGG": MaGG,
                    "Hinhthuc": hinhthuc_str,
                    "LoaiGG": loaigg,
                    "GiaTri": gia_tri,
                    "SoLuong": so_luong,
                    "NgayBD": ngay_bd,
                    "NgayKT": ngay_kt,
                    "TrangThai": "Active",
                    "admin_id": current_user.id,
                    "DieuKien": dieu_kien,
                    "DieuKienSP": dieu_kien_sp
                }

                if add_voucher(data):
                    flash(f"Thêm voucher thành công mã {MaGG}!", "success")
                    return redirect('/admin')  # ✅ PASS test success

                flash("Lỗi DB!", "danger")
                return redirect('/create')

            # 👉 GET
            categories = dao.load_categories()
            return render_template("admin/create_voucher.html", categories=categories)

        except Exception as e:
            app.logger.error(f"Lỗi Add Voucher: {e}")
            flash("Lỗi hệ thống!", "danger")
            return redirect('/create')
    # edit voucher
    # Route 1: Mở trang sửa (đổ dữ liệu vào create.html)
    @app.route('/edit/<string:ma_gg>')
    def edit_voucher_view(ma_gg):
        v_edit = dao.get_voucher_by_id(ma_gg)
        categories = dao.load_categories()
        if v_edit:
            return render_template('admin/create_voucher.html', v_edit=v_edit,c=categories)
        flash("Không tìm thấy mã giảm giá!", "danger",)
        return redirect('/admin')

    # update voucher
    @app.route('/update/<string:ma_gg>', methods=['POST'])
    def update_voucher_route(ma_gg):
        try:
            # BƯỚC 1: Lấy dữ liệu thô (Dạng chuỗi) - KHÔNG ép kiểu vội
            raw_gia_tri = request.form.get('GiaTri')
            raw_so_luong = request.form.get('SoLuong')
            loaigg = request.form.get('LoaiGG')
            hinh_thuc = request.form.get('Hinhthuc')
            dieu_kien_sp = (request.form.get('DieuKienSP')or None)
            raw_dieu_kien = request.form.get('DieuKien')
            ngay_bd_str = request.form.get('NgayBD')
            ngay_kt_str = request.form.get('NgayKT')

            # BƯỚC 2: Kiểm tra Rỗng TRƯỚC khi tính toán
            if not raw_gia_tri or not raw_so_luong or not loaigg or not hinh_thuc:
                flash("Vui lòng nhập đầy đủ thông tin!", "danger")
                return redirect(f'/edit/{ma_gg}')

            # BƯỚC 3: Ép kiểu an toàn sau khi đã chắc chắn không rỗng
            try:
                gia_tri = float(raw_gia_tri or 0)
                so_luong = int(raw_so_luong)
                dieu_kien = float(raw_dieu_kien or 0)

                ngay_bd = datetime.strptime(ngay_bd_str, "%Y-%m-%dT%H:%M") if ngay_bd_str else None
                ngay_kt = datetime.strptime(ngay_kt_str, "%Y-%m-%dT%H:%M") if ngay_kt_str else None
            except (ValueError, TypeError):
                flash("Định dạng dữ liệu số hoặc ngày tháng không đúng!", "danger")
                return redirect(f'/edit/{ma_gg}')
            valid_types = ["Khuyến mãi", "Shipping"]


            # BƯỚC 4: Ràng buộc nghiệp vụ (Business Logic)
            if hinh_thuc not in valid_types:
                flash("Hình thức giảm giá không hợp lệ!", "danger")
                return redirect(f'/edit/{ma_gg}')

            # Fix lỗi ưu tiên toán tử: (A or B) and (C or D)
            if (loaigg == "phần trăm" or loaigg == "phantram") and (gia_tri <= 0 or gia_tri > 50):
                flash("Phần trăm giảm giá phải từ 1 đến 50!", "danger")
                return redirect(f'/edit/{ma_gg}')

            if (loaigg == "tien" or loaigg == "tiền") and (gia_tri < 10000 or gia_tri > 20000000):
                flash("Số tiền giảm phải từ 10.000vnđ đến 20.000.000vnđ", "danger")
                return redirect(f'/edit/{ma_gg}')

            if so_luong <= 0 or so_luong > 1000:
                flash("Số lượng phát hành không hợp lệ", "danger")
                return redirect('/create')

            # BƯỚC 5: Xử lý thời gian
            ngay_bd = datetime.strptime(ngay_bd_str, "%Y-%m-%dT%H:%M") if ngay_bd_str else None
            ngay_kt = datetime.strptime(ngay_kt_str, "%Y-%m-%dT%H:%M") if ngay_kt_str else None

            if not ngay_bd or not ngay_kt:
                flash("Vui lòng nhập đầy đủ ngày bắt đầu và ngày kết thúc!", "danger")
                return redirect(f'/edit/{ma_gg}')

            if ngay_kt <= ngay_bd:
                flash("Ngày kết thúc phải lớn hơn ngày bắt đầu!", "danger")
                return redirect(f'/edit/{ma_gg}')

            if ngay_kt < datetime.now():
                flash("Ngày kết thúc không được ở quá khứ!", "danger")
                return redirect(f'/edit/{ma_gg}')

            # BƯỚC 6: Gom data và gọi DAO

            # Tính TrangThai tự động theo ngày
            now = datetime.now()
            if ngay_bd and ngay_kt:
                if now < ngay_bd:
                    trang_thai = "Pending"
                elif now > ngay_kt:
                    trang_thai = "Expired"
                else:
                    trang_thai = "Active"
            else:
                trang_thai = "Inactive"

            data = {
                "Hinhthuc": hinh_thuc,
                "LoaiGG": loaigg,
                "GiaTri": gia_tri,
                "SoLuong": so_luong,
                "NgayBD": ngay_bd,
                "NgayKT": ngay_kt,
                "TrangThai": trang_thai,
                "MoTa": request.form.get('MoTa'),
                "DieuKien": float(request.form.get('DieuKien') or 0),
                "DieuKienSP": dieu_kien_sp
            }

            if dao.update_voucher(ma_gg, data):
                flash(f"Cập nhật mã {ma_gg} thành công!", "success")
                return redirect('/admin')
            else:
                flash("Có lỗi xảy ra khi lưu dữ liệu vào Database!", "danger")
                return redirect(f'/edit/{ma_gg}')

        except Exception as e:
            flash(f"Lỗi hệ thống: {str(e)}", "danger")
            return redirect(f'/edit/{ma_gg}')

    @app.route('/delete/<maGG>', methods=['POST'])
    @login_required
    def delete_voucher(maGG):
        if int(current_user.user_role) != UserRole.ADMIN:
            flash("Bạn không có quyền thực hiện thao tác này!", "danger")
            return redirect('/admin')

        try:
            voucher = dao.get_voucher_by_id(maGG)
            if not voucher:
                flash("Voucher không tồn tại!", "danger")
                return redirect('/admin')

            now = datetime.now()

            # Chuẩn hóa dữ liệu
            voucher.DaSuDung = voucher.DaSuDung or 0
            voucher.SoLuong = voucher.SoLuong or 0

            # Logic xóa
            het_han = voucher.NgayKT and now > voucher.NgayKT
            da_dung_het = voucher.DaSuDung == voucher.SoLuong
            chua_su_dung = voucher.DaSuDung == 0
            unlimited = voucher.SoLuong is None

            can_delete = het_han or da_dung_het or chua_su_dung

            if not can_delete:
                flash(f"Không thể xóa mã {maGG} vì đang được sử dụng!", "warning")
                return redirect('/admin')

            if voucher.NgayKT < datetime.now():
                message = f"Voucher {voucher.MaGG} đã hết hạn nên được xóa!"
            elif unlimited:
                message = f"Voucher {voucher.MaGG} không giới hạn nên được xóa!"
            else:
                message = f"Xóa thành công voucher {maGG}!"

            db.session.delete(voucher)
            db.session.commit()
            flash(message, "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Lỗi hệ thống: {str(e)}", "danger")

        return redirect('/admin')
    #---------------- ---GIỏ hàng----------------------
    @app.route("/cart")
    def cart():
        # session['cart'] = {
        #     "1":{
        #         "id":"1",
        #         "id":"1",
        #         "name":"Mì Gói",
        #         "price":100000,
        #         "quantity":1,
        #     },
        #     "2": {
        #         "id": "2",
        #         "name": "Kem",
        #         "price": 20000,
        #         "quantity": 3,
        #     }
        # }
        vouchers = dao.get_all_vouchers_active()  # Lấy tất cả voucher từ DB
        # Lọc thành 2 nhóm
        promo_v = [v for v in vouchers if 'shipping' not in v.Hinhthuc.lower()]
        ship_v = [v for v in vouchers if 'shipping' in v.Hinhthuc.lower()]
        return render_template('customer/cart.html',
                               promotion_vouchers=promo_v,
                               shipping_vouchers=ship_v,
                               cart=utils.cart_stash(session.get('cart')))
    # thêm vào giỏ
    @app.route('/api/cart', methods=['post'])
    def add_to_cart():
        data = request.json
        id = str(data['id'])
        key = app.config['CART_KEY']
        cart = session[key] if key in session else {}

        if id in cart:
            cart[id]['quantity'] += 1
        else:
            name = data['name']
            price = data['price']
            image = data['image']
            category_id = data.get('category_id')

            cart[id] = {
                "id":id,
                "name": name,
                "price": price,
                "image": image,
                "category_id": category_id,
                "quantity": 1
            }

        session[key] = cart
        session.modified = True

        res = utils.cart_stash(cart=cart)

        res['status'] = 200
        return jsonify(res)

    # cập nhật giỏ hàng
    @app.route('/api/cart/<product_id>', methods=['put'])
    def update_cart(product_id):
        data = request.json
        raw_quantity = data.get('quantity')  # Lấy số lượng mới từ request

        key = app.config['CART_KEY']
        cart = session.get(key)
        try:
            quantity = int(raw_quantity)
        except (ValueError, TypeError):
            return jsonify({"error": "Số lượng không hợp lệ"}), 400

        if cart and product_id in cart:
            if quantity > 0:
                cart[product_id]['quantity'] = quantity
            else:
                del cart[product_id]

            session.modified = True
            session[key] = cart

        return jsonify(utils.cart_stash(cart=cart))

    # xóa sp khỏi giỏ hàng
    @app.route('/api/cart/<product_id>', methods=['delete'])
    def delete_cart(product_id):
        key = app.config['CART_KEY']
        cart = session.get(key)

        if cart and product_id in cart:
            del cart[product_id]

        session[key] = cart

        return jsonify(utils.cart_stash(cart=cart))

    # áp dụng voucher
    @app.route('/api/apply-voucher/<voucherId>', methods=['PUT'])
    def apply_voucher(voucherId):
        data = request.json
        magg = data.get('voucher_id')
        v = dao.get_voucher_by_id(magg)
        cart = session.get(app.config.get('CART_KEY', 'cart'))

        if not cart:
            return jsonify({"status": 404, "message": "Giỏ hàng đang trống!"})

        if v:
            cart_stats = utils.cart_stash(cart)
            total_price = cart_stats['total_price']
            # lấy tổng tiền so với điều kiện tối thiểu
            if total_price < v.DieuKien:
                price = "{:,.0f}".format(v.DieuKien)
                return jsonify({
                    "status": 404,
                    "message": f"Đơn hàng phải tối thiểu {price} VNĐ mới dùng được!"
                })
            # so sánh danh mục có khớp với điều kiện sp danh mục ko
            if v.DieuKienSP:
                target_cate = str(v.DieuKienSP).strip()
                categories_in_cart = {
                    str(item.get('category_id')).strip()
                    for item in cart.values()
                    if item.get('category_id') is not None
                }
                cate = dao.get_category_by_id(int(target_cate))
                cate_name = cate.name if cate else target_cate
                if target_cate not in categories_in_cart:
                    return jsonify({
                        "status": 404,
                        "message": f"Voucher này chỉ áp dụng cho sản phẩm thuộc danh mục {cate_name}"
                    })
            now = datetime.now()

            #  kiểm tra ngày bắt đầu
            if v.NgayBD and now < v.NgayBD:
                start_date = v.NgayBD.strftime('%d/%m/%Y %H:%M')
                return jsonify({
                    "status": 404,
                    "message": f"Mã này chưa đến hạn sử dụng. Vui lòng quay lại vào lúc {start_date} nhé!"
                })

            # kiểm tra ngày kết thúc
            if v.NgayKT and now > v.NgayKT:
                return jsonify({
                    "status": 404,
                    "message": "Mã giảm giá này đã hết hạn sử dụng rồi!"
                })
            # kiếm tra số lượng voucher hiện tại so với lượt đã sử dụng
            if v.SoLuong is not None and v.SoLuong > 0:
                if v.DaSuDung >= v.SoLuong:
                    return jsonify({
                        "status": 404,
                        "message": "Rất tiếc, mã này hết lượt sử dụng rồi!"
                    })
            # kiếm tra hết điều kiện rồi thì mới đc apply
            applied_vouchers = session.get('applied_vouchers', {})
            kind = 'SHIPPING' if 'shipping' in v.Hinhthuc.lower() else 'PROMOTION'
            applied_vouchers[kind] = {
                "MaGG": v.MaGG,
                "LoaiGG": v.LoaiGG,
                "GiaTri": float(v.GiaTri)
            }
            session['applied_vouchers'] = applied_vouchers
            session.modified = True

            cart_stats = utils.cart_stash(cart)
            res = utils.calculate_multi_vouchers(session['applied_vouchers'], cart_stats['total_price'])
            res['applied_vouchers'] = session['applied_vouchers']
            res['status'] = 200
            res['message'] = f"Đã áp dụng mã {v.MaGG} thành công!"
            return jsonify(res)

        return jsonify({"status": 404, "message": "Mã không tồn tại!"})
    # xóa mã đã chọn
    @app.route('/api/apply-voucher/', methods=['delete'])
    def delete_apply_voucher():
        session['applied_vouchers'] = {}
        session.modified = True

        cart = session.get(app.config.get('CART_KEY'), {})
        cart_stats = utils.cart_stash(cart)
        return jsonify({
            "status": 200,
            "total_price": cart_stats['total_price'],
            "message": "Đã xóa sạch mã"
        })

    @app.context_processor
    def common_attr():
        categories = dao.load_categories()
        return {
            "categories": categories,
            'cart':utils.cart_stash(session.get(app.config['CART_KEY'])),
        }
    #Thanh toán đơn hàng
    @app.route('/api/checkout', methods=['POST'])
    @login_required
    def checkout_api():
        cart = session.get(app.config.get('CART_KEY', 'cart'))
        applied_vouchers = session.get('applied_vouchers', {})

        if not cart:
            return jsonify({"status": 404, "message": "Giỏ hàng trống!"})

        data = request.json
        ten_nguoi_nhan = data.get('name')
        sdt = data.get('phone')
        dia_chi = data.get('address')
        hinh_thuc_tt = data.get('payment_method', 'Tiền mặt')
        if not ten_nguoi_nhan:
            return jsonify({"status": 400, "message": "Vui lòng nhập đầy đủ tên!"})
        if not sdt :
            return jsonify({"status": 400, "message": "Vui lòng nhập đầy đủ SĐT!"})
        if not dia_chi:
            return jsonify({"status": 400, "message": "Vui lòng nhập đầy đủ địa chỉ!"})
        sdt_pattern = r"^0\d{9,10}$"
        if not sdt or not re.match(sdt_pattern, sdt):
            return jsonify({
                "status": 400,
                "message": "Số điện thoại không hợp lệ! Phải bắt đầu bằng số 0 và chỉ chứa số."
            })
        try:
            # tính tiền và mức giảm cuối cùng
            cart_stats = utils.cart_stash(cart)
            total_price_raw = cart_stats['total_price']
            voucher_results = utils.calculate_multi_vouchers(applied_vouchers, total_price_raw)

            don_hang = dao.add_receipt(
                cart=cart,
                user=current_user,
                hinh_thuc_tt=hinh_thuc_tt,
                applied_vouchers=applied_vouchers,
                total_after_discount=voucher_results['new_price'],
                receiver_info={
                    "name": ten_nguoi_nhan,
                    "phone": sdt,
                    "address": dia_chi
                }
            )

            if don_hang:
                # cập nhật lại session
                session[app.config['CART_KEY']] = {}
                session['applied_vouchers'] = {}
                session.modified = True
                name = current_user.name
                return jsonify({
                    "status": 200,
                    "message": f"Đặt hàng thành công! Cảm ơn {name} đã ủng hộ.",
                    "order_id": don_hang.id
                })

        except Exception as ex:
            print(f"Lỗi thanh toán: {str(ex)}")
            return jsonify({"status": 500, "message": "Lỗi hệ thống khi tạo đơn hàng!"})

        return jsonify({"status": 500, "message": "Không thể hoàn tất thanh toán!"})
    # danh sach voucher hiển thị bên khách hàng
    @app.route('/voucher-list')
    @login_required
    def VoucherList():
        # Lấy tất cả voucher đang Active
        vouchers = dao.get_all_vouchers()
        now = datetime.now()

        promotion_vouchers = []
        shipping_vouchers = []

        for v in vouchers:
            trang_thai_db = str(v.TrangThai or "").lower().strip()

            # Bỏ qua không hiển thị nếu voucher bị vô hiệu hóa/đã xóa

            # Chỉ lấy những mã chưa hết hạn ngày kết thúc
            if not v.NgayKT or now <= v.NgayKT :
                # Tính số lượng còn lại (đảm bảo không bị âm)
                v.con_lai = max(0, v.SoLuong-v.DaSuDung)
                # Biến kiểm tra xem còn lượt dùng hay không
                v.is_available = v.con_lai > 0
                if trang_thai_db in ['pending', 'inactive'] or (v.NgayBD and now < v.NgayBD):
                    v.is_pending = True
                    v.status = 'pending'

                    if v.NgayBD:
                        v.ngay_bat_dau_str = v.NgayBD.strftime('%d/%m/%Y %H:%M')
                    else:
                        v.ngay_bat_dau_str = "Sắp tới"
                else:
                    v.is_pending = False
                    v.status = 'active'
                # Phân loại theo Hinhthuc
                hinh_thuc_str = str(v.Hinhthuc or "").lower().strip()
                if 'ship' in hinh_thuc_str or 'vận chuyển' in hinh_thuc_str:
                    shipping_vouchers.append(v)
                else:
                    promotion_vouchers.append(v)

        return render_template('customer/voucher-list.html',
                               promotion_vouchers=promotion_vouchers,
                               shipping_vouchers=shipping_vouchers)



    #  AUTH & LOGIN ---
    @app.route("/login", methods=['GET', 'POST'])
    def user_login():
        if current_user.is_authenticated:
            return redirect('/admin' if int(current_user.user_role) == 1 else '/')
        err_msg = None
        if request.method == 'POST':
            user = dao.auth_user(request.form.get("role"), request.form.get("username"), request.form.get("password"))
            if user:
                login_user(user)
                return redirect('/admin' if int(user.user_role) == 1 else '/')
            err_msg = "Sai tài khoản hoặc mật khẩu!"
        return render_template("login.html", err_msg=err_msg)

    @app.route("/register",  methods=['get', 'post'])
    def register():
        err_msg = None

        if request.method.__eq__("POST"):
            name = request.form.get("name")
            username = request.form.get("username")
            password = request.form.get("password")
            confirm = request.form.get("confirm")
            email = request.form.get('email')

            password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

            if not name or not name.strip():
                err_msg = "Họ tên không được để trống!"
            elif not username or not username.strip():
                err_msg = "Tên tài khoản không được để trống!"
            elif " " in username:
                err_msg = "Tên tài khoản không được chứa khoảng trắng!"
            elif not re.match("^[A-Za-z0-9]+$", username):
                err_msg = "Tên tài khoản không được chứa ký tự đặc biệt!"
            elif dao.check_username_exists(username):
                err_msg = "Tên đăng nhập này đã tồn tại! Vui lòng chọn tên khác."
            elif not re.match(password_pattern, password):
                err_msg = ("Mật khẩu phải có ít nhất 8 ký tự. Gồm chữ hoa, chữ thường, số, ký tự đặc biệt.")
            elif not password.__eq__(confirm):
                err_msg = "Mật khẩu không khớp!"
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                err_msg = "Định dạng email không hợp lệ!"
            else:
                name = request.form.get("name")
                username = request.form.get("username")
                avatar = request.files.get("avatar")
                path_file = None
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    path_file = res["secure_url"]
                try:
                    dao.add_user(name, username, password, email, avatar=path_file)
                    return redirect('/login')
                except:
                    db.session.rollback()
                    err_msg = "Hệ thống đang có lỗi! Vui lòng quay lại sau!"
        return render_template("register.html", err_msg=err_msg)



    @app.route('/logout')
    def user_logout():
        logout_user()
        return redirect('/')


    @app.route('/api/send-otp', methods=['POST'])
    def send_otp():
        data = request.json
        username = data.get('username')
        email = data.get('email')

        # 1. Kiểm tra thông tin khớp trong DB
        user = dao.get_user(username, email)

        if not user:
            return jsonify({
                "success": False,
                "message": "Thông tin không khớp! Kiểm tra lại Username hoặc Email"
            })

        try:
            # 2. Tạo mã OTP ngẫu nhiên 6 số
            otp_code = str(random.randint(100000, 999999))

            # 3. Lưu vào bộ nhớ tạm để kiểm tra sau này (dùng email làm key)
            otp_storage[email] = otp_code

            # Lấy đối tượng mail từ current_app
            mail = current_app.extensions.get('mail')

            if not mail:
                # Nếu vẫn không thấy, tự tạo mock object
                from flask_mail import Mail
                mail = Mail(current_app)

            # 4. Soạn thảo và gửi Email
            msg = Message(
                subject='[BACH HOA SHOP] Mã xác thực OTP đặt lại mật khẩu',
                recipients=[email],
                body=f"Chào {user.name},\n\nMã OTP để đặt lại mật khẩu của bạn là: {otp_code}\n\nMã này sẽ hết hạn khi bạn đóng trình duyệt. Vui lòng không chia sẻ mã này cho ai."
            )
            mail.send(msg)

            return jsonify({"success": True, "message": "OTP đã được gửi! Bạn kiểm tra hòm thư nhé."})

        except Exception as e:
            print(f"Lỗi gửi mail: {str(e)}")
            return jsonify({"success": False, "message": "Lỗi hệ thống khi gửi mail. Thử lại sau nhé!"})
    # Api xác nhận OTP và đổi mật khẩu
    @app.route('/api/verify-reset', methods=['POST'])
    def verify_reset():
        data = request.get_json()
        email = data.get('email')
        otp_input = data.get('otp')
        new_password = data.get('new_password')
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

              # 1. Kiểm tra OTP
        # Nếu email không có trong kho hoặc OTP sai
        if email not in otp_storage or otp_storage[email] != otp_input:
            return jsonify({'success': False, 'message': 'Mã OTP không đúng hoặc đã hết hạn!'})
        if not re.match(password_pattern, new_password):
            return jsonify({
                "success": False,
                "message": "Mật khẩu phải có ít nhất 8 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
            })

        # 2. Gọi DAO cập nhật mật khẩu mới
        if dao.update_password(email, new_password):
            # 3. Xóa OTP sau khi dùng xong để bảo mật
            del otp_storage[email]
            return jsonify({'success': True, 'message': 'Đổi mật khẩu thành công! Hãy đăng nhập lại.'})
        else:
            return jsonify({'success': False, 'message': 'Lỗi hệ thống khi cập nhật mật khẩu.'})

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_userid(int(user_id))

if __name__ == "__main__":
    register_routes(app=app)
    app.run(debug=True)