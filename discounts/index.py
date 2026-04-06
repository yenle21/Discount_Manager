import random
import re
import cloudinary
import cloudinary.uploader
import datetime
import math
import json
from flask import render_template, session, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message, Mail
from dao import load_products, load_categories, add_voucher, get_voucher_by_id
from discounts import app, db, login, dao
from discounts.models import UserRole, Voucher, CTHD, DonHang, Product, Category,User
from datetime import datetime

otp_storage = {}
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nhu.nt2508@gmail.com'  # <-- Email của bạn
app.config['MAIL_PASSWORD'] = 'jtpq brbn wldf ywrl'   # <-- Mật khẩu ứng dụng của bạn
app.config['MAIL_DEFAULT_SENDER'] = 'nhu.nt2508@gmail.com'


mail = Mail(app) # Khởi tạo mail server



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


#Quỳnh Như tạo voucher
@app.route("/create")
def create():
    categories = dao.load_categories()
    return render_template("admin/create_voucher.html", categories=categories)


@app.route('/admin')
def admin_voucher():
    trang_thai = request.args.get('trang_thai')
    hinh_thuc = request.args.get('hinh_thuc')
    kw = request.args.get('kw')
    vouchers = Voucher.query.all()
    now = datetime.now()

    filtered = []
    hinh_thuc_list = set()  # lấy danh sách unique

    for v in vouchers:
        # ===== SEARCH =====
        if kw:
            if kw.lower() not in (v.MaGG or "").lower() and \
                    kw.lower() not in (v.MoTa or "").lower():
                continue

        # ===== lấy danh sách hình thức =====
        if v.Hinhthuc:
            hinh_thuc_list.add(v.Hinhthuc)

        # ===== xử lý trạng thái =====
        if v.NgayBD and now < v.NgayBD:
            status = "pending"
        elif v.NgayKT and now > v.NgayKT:
            status = "expired"
        else:
            status = "active"

        v.TrangThai = status

        # ===== filter =====
        if trang_thai and status != trang_thai:
            continue

        if hinh_thuc and v.Hinhthuc != hinh_thuc:
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

@app.route('/add', methods=['POST'])
def add_voucher_route():
    try:
        MaGG = request.form.get('MaGG')

        # check trùng
        if get_voucher_by_id(MaGG):
            flash("Mã voucher đã tồn tại!", "danger")
            return redirect('/create')

        # convert datetime
        ngay_bd = request.form.get('NgayBD')
        ngay_kt = request.form.get('NgayKT')

        ngay_bd = datetime.strptime(ngay_bd, "%Y-%m-%dT%H:%M") if ngay_bd else None
        ngay_kt = datetime.strptime(ngay_kt, "%Y-%m-%dT%H:%M") if ngay_kt else None

        data = {
            "MaGG": MaGG,
            "Hinhthuc": request.form.get('Hinhthuc'),
            "LoaiGG": request.form.get('LoaiGG'),
            "GiaTri": float(request.form.get('GiaTri') or 0),
            "SoLuong": int(request.form.get('SoLuong') or 0),
            "NgayBD": ngay_bd,
            "NgayKT": ngay_kt,
            "TrangThai": "Active" if request.form.get('TrangThai') == "active" else "Inactive",
            "MoTa": request.form.get('MoTa'),
            "admin_id": 1,
            "DieuKien": float(request.form.get('DieuKien') or 0),
            "DieuKienSP": request.form.get('DieuKienSP')
        }


        if add_voucher(data):
            flash("Thêm voucher thành công!", "success")
            return redirect('/admin')
        else:
            flash("Lỗi khi lưu DB!", "danger")
            return redirect('/create')

    except Exception as e:
        print(e)
        flash("Lỗi hệ thống!", "danger")
        return redirect('/create')


@app.route('/api/vouchers')
def get_vouchers_api():
    # Lấy thông tin để lọc mã phù hợp với giỏ hàng hiện tại
    total_amount = float(request.args.get('total', 0))
    categories_str = request.args.get('categories', '')
    current_category_ids = categories_str.split(',') if categories_str else []

    # Chỉ lấy các mã đang hoạt động
    vouchers = Voucher.query.filter(Voucher.TrangThai == 'Active').all()
    output = []

    for v in vouchers:
        # 1. Kiểm tra số lượng lượt dùng còn lại
        if v.SoLuong is not None and v.DaSuDung >= v.SoLuong:
            continue

        # 2. Kiểm tra tổng đơn hàng tối thiểu
        if v.DieuKien and total_amount < v.DieuKien:
            continue

        # 3. Kiểm tra danh mục sản phẩm (nếu có yêu cầu)
        if v.DieuKienSP:
            if v.DieuKienSP not in current_category_ids:
                continue

        output.append({
            "code": v.MaGG,
            "type": v.Hinhthuc,
            "value": v.GiaTri,
            "condition": v.DieuKien,
            "description": v.MoTa,
            "expiry": v.NgayKT.strftime('%d/%m/%Y') if v.NgayKT else "Vô thời hạn"
        })
    return jsonify(output)


@app.route('/api/apply-voucher', methods=['POST'])
def apply_voucher_api():
    data = request.json
    code = data.get('code')
    total_amount = float(data.get('total_amount', 0))

    v = db.session.get(Voucher, code)
    if not v or v.TrangThai != 'Active':
        return jsonify({"status": 400, "message": "Mã không tồn tại hoặc đã bị tắt!"})

    # Kiểm tra lại điều kiện một lần nữa trước khi áp dụng
    if v.SoLuong is not None and v.DaSuDung >= v.SoLuong:
        return jsonify({"status": 400, "message": "Mã đã hết lượt sử dụng!"})

    if v.DieuKien and total_amount < v.DieuKien:
        return jsonify({"status": 400, "message": f"Đơn hàng chưa đủ {v.DieuKien:,.0f}đ"})

    # Tăng số lượng đã sử dụng lên 1 ngay khi bấm "Sử dụng"
    v.DaSuDung += 1
    db.session.commit()

    # Lưu vào session để checkout và đánh dấu 'locked' để không cho xóa ở giao diện
    if 'applied_vouchers' not in session:
        session['applied_vouchers'] = {}

    session['applied_vouchers'][v.MaGG] = {
        'code': v.MaGG,
        'discount_amount': (total_amount * (v.GiaTri / 100)) if v.Hinhthuc == "Phần trăm" else v.GiaTri,
        'locked': True
    }
    session.modified = True

    return jsonify({
        "status": 200,
        "message": f"Áp dụng mã {code} thành công!",
        "applied_details": session['applied_vouchers']
    })


# --- QUẢN LÝ VOUCHER CHO ADMIN ---
@app.route('/delete/<maGG>', methods=['POST'])
@login_required
def delete_voucher(maGG):
    if int(current_user.user_role) != UserRole.ADMIN:
        return jsonify({"status": 403, "message": "Không có quyền!"})

    try:
        voucher = Voucher.query.get(maGG)
        if not voucher:
            flash("Voucher không tồn tại!", "danger")
            return redirect('/admin')

        # CHẶN XÓA NẾU ĐÃ CÓ NGƯỜI DÙNG (Bảo vệ dữ liệu)
        if voucher.DaSuDung and voucher.DaSuDung > 0:
            flash(f"Không thể xóa mã {maGG} vì đã có {voucher.DaSuDung} lượt sử dụng!", "warning")
            return redirect('/admin')

        db.session.delete(voucher)
        db.session.commit()
        flash("Xóa voucher thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Lỗi hệ thống: {str(e)}", "danger")

    return redirect('/admin')
######## QNhu


# --- 2. GIỎ HÀNG & CẬP NHẬT SỐ LƯỢNG ---
@app.route("/cart")
def cart():
    categories = dao.load_categories()
    cart_data = session.get('cart', {})

    total_amount = sum(item['quantity'] * item['price'] for item in cart_data.values())
    total_quantity = sum(item['quantity'] for item in cart_data.values())

    return render_template("customer/cart.html",
                           categories=categories,
                           cart=cart_data,
                           total_amount=total_amount,
                           total_quantity=total_quantity)


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    p_id = str(data.get('id'))
    if not p_id: return jsonify({"status": 400, "message": "Thiếu ID!"})

    cart = session.get('cart', {})
    if p_id in cart:
        cart[p_id]['quantity'] += 1
    else:
        # Lấy thêm category_id lưu vào session để check voucher nhanh hơn
        product = db.session.get(Product, int(p_id))
        cart[p_id] = {
            "id": p_id,
            "name": data.get('name'),
            "price": data.get('price'),
            "image": data.get('image'),
            "category_id": product.category_id if product else None,
            "quantity": 1
        }
    session['cart'] = cart
    return jsonify({"total_quantity": sum(item['quantity'] for item in cart.values()), "status": 200})


@app.route('/api/update-cart', methods=['POST'])
def update_cart():
    data = request.json
    p_id, delta = str(data.get('id')), data.get('delta')
    cart = session.get('cart', {})

    if p_id in cart:
        cart[p_id]['quantity'] += delta
        if cart[p_id]['quantity'] <= 0: del cart[p_id]
        session['cart'] = cart
        session.modified = True

    total_amount = sum(item['quantity'] * item['price'] for item in cart.values())
    return jsonify({
        "status": 200,
        "total_quantity": sum(item['quantity'] for item in cart.values()),
        "total_amount": total_amount,
        "new_qty": cart[p_id]['quantity'] if p_id in cart else 0
    })


# # --- 3. LOGIC VOUCHER (SHOPEE STYLE) ---
# @app.route('/api/vouchers')
# def get_vouchers():
#     vouchers = Voucher.query.all()
#     output = []
#     for v in vouchers:
#         output.append({
#             "code": v.MaGG,
#             "type": v.Hinhthuc,
#             "condition": v.DieuKien,
#             "expiry": v.NgayKT.strftime('%d/%m/%Y') if v.NgayKT else "Không hết hạn",
#             "category_id": v.DieuKienSP,
#             "description": v.MoTa # THÊM DÒNG NÀY ĐỂ HIỆN MÔ TẢ
#         })
#     return jsonify(output)
#
# @app.route('/api/apply-voucher', methods=['POST'])
# def apply_voucher():
#     data = request.json
#     code = data.get('code')
#     total_amount = float(data.get('total_amount', 0))
#     cart = session.get('cart', {})
#
#     if 'applied_vouchers' not in session:
#         session['applied_vouchers'] = {'SHIPPING': None, 'PROMOTION': None}
#
#     # CASE: Tính toán lại khi giỏ hàng thay đổi (Fix lỗi tiền âm của Yến)
#     if code == "RE_CALCULATE":
#         total_discount = 0
#         for v_type, v_info in list(session['applied_vouchers'].items()):
#             if v_info:
#                 v_db = db.session.get(Voucher, v_info['code'])
#                 if v_db and (not v_db.DieuKien or total_amount >= v_db.DieuKien):
#                     new_disc = (total_amount * (v_db.GiaTri / 100)) if v_db.Hinhthuc == "Phần trăm" else v_db.GiaTri
#                     v_info['discount_amount'] = new_disc
#                     total_discount += new_disc
#                 else:
#                     session['applied_vouchers'][v_type] = None
#         session.modified = True
#         return jsonify({"status": 200, "total_discount": total_discount, "new_total": total_amount - total_discount,
#                         "applied_details": session['applied_vouchers']})
#
#     # CASE: Áp dụng mã mới
#     v = db.session.get(Voucher, code)
#     if not v or v.TrangThai != 'Active': return jsonify({"status": 400, "message": "Mã không tồn tại!"})
#
#     now = datetime.datetime.now()
#     if (v.NgayBD and now < v.NgayBD) or (v.NgayKT and now > v.NgayKT): return jsonify(
#         {"status": 400, "message": "Mã hết hạn!"})
#     if v.DieuKien and total_amount < v.DieuKien: return jsonify(
#         {"status": 400, "message": f"Đơn tối thiểu {v.DieuKien:,.0f}đ!"})
#
#     # Check danh mục sản phẩm
#     if v.DieuKienSP:
#         target_cat = int(v.DieuKienSP)
#         if not any(int(item.get('category_id', 0)) == target_cat for item in cart.values()):
#             return jsonify({"status": 400, "message": "Không có sản phẩm thuộc danh mục ưu đãi!"})
#
#     v_type = 'SHIPPING' if v.Hinhthuc in ['SHIPPING', 'Vận chuyển'] else 'PROMOTION'
#     this_discount = (total_amount * (v.GiaTri / 100)) if v.Hinhthuc == "Phần trăm" else v.GiaTri
#
#     session['applied_vouchers'][v_type] = {'code': v.MaGG, 'discount_amount': this_discount, 'hinh_thuc': v.Hinhthuc}
#     session.modified = True
#
#     total_discount = sum(item['discount_amount'] for item in session['applied_vouchers'].values() if item)
#     return jsonify({"status": 200, "message": f"Áp dụng {v.MaGG} thành công!", "total_discount": total_discount,
#                     "new_total": total_amount - total_discount, "applied_details": session['applied_vouchers']})
#

@app.route('/api/clear-vouchers', methods=['POST'])
def clear_vouchers():
    session.pop('applied_vouchers', None)
    return jsonify({"status": 200})


# --- 4. THANH TOÁN (CHECKOUT) ---
@app.route('/api/checkout', methods=['POST'])
@login_required
def checkout_api():
    data = request.json
    cart = session.get('cart')
    if not cart: return jsonify({"status": 400, "message": "Giỏ hàng trống!"})

    applied_v = session.get('applied_vouchers', {})
    voucher_codes = [v['code'] for v in applied_v.values() if v]

    try:
        new_order = DonHang(HinhThucTT=data.get('payment_method'), khach_hang_id=current_user.id,
                            ma_giam_gia_id=", ".join(voucher_codes) if voucher_codes else None, TrangThai="Processing")
        db.session.add(new_order)
        db.session.flush()

        for p_id, item in cart.items():
            db.session.add(CTHD(MaSP=int(p_id), MaHD=new_order.id, SoLuong=item['quantity'],
                                TongTien=item['quantity'] * item['price'], TenNguoiNhan=data.get('name'),
                                SDT=data.get('phone'), DiaChi=data.get('address')))

        # Cập nhật số lần dùng Voucher
        for v_info in applied_v.values():
            if v_info:
                v = db.session.get(Voucher, v_info['code'])
                if v: v.DaSuDung += 1

        db.session.commit()
        session.pop('cart', None)
        session.pop('applied_vouchers', None)
        return jsonify({"status": 200, "message": "Đặt hàng thành công!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": 500, "message": str(e)})


# --- 5. AUTH & LOGIN ---
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
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get('email')

        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        # import pdb #kiểm tra lỗi
        # pdb.set_trace()

        if dao.check_username_exists(username):
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

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(int(user_id))

@app.route('/logout')
def user_logout():
    logout_user()
    return redirect('/')
@app.route('/admin')
@login_required
def admin():
   return render_template("admin/admin.html")

@app.route('/create')
@login_required
def create_voucher():
    return  render_template("admin/create_voucher.html")


@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    username = data.get('username')
    email = data.get('email')

    # 1. Kiểm tra thông tin khớp trong DB
    user = User.query.filter_by(username=username, email=email).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "Thông tin không khớp! Kiểm tra lại Username hoặc Email nhé Yến."
        })

    try:
        # 2. Tạo mã OTP ngẫu nhiên 6 số
        otp_code = str(random.randint(100000, 999999))

        # 3. Lưu vào bộ nhớ tạm để kiểm tra sau này (dùng email làm key)
        otp_storage[email] = otp_code

        # 4. Soạn thảo và gửi Email
        msg = Message(
            subject='[BACH HOA SHOP] Mã xác thực OTP đặt lại mật khẩu',
            recipients=[email],
            body=f"Chào {user.name},\n\nMã OTP để đặt lại mật khẩu của bạn là: {otp_code}\n\nMã này sẽ hết hạn khi bạn đóng trình duyệt. Vui lòng không chia sẻ mã này cho ai."
        )
        mail.send(msg)

        return jsonify({"success": True, "message": "OTP đã được gửi! Yến kiểm tra hòm thư nhé."})

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

    # 1. Kiểm tra OTP
    # Nếu email không có trong kho hoặc OTP sai
    if email not in otp_storage or otp_storage[email] != otp_input:
        return jsonify({'success': False, 'message': 'Mã OTP không đúng hoặc đã hết hạn!'})

    # 2. Gọi DAO cập nhật mật khẩu mới
    if dao.update_password(email, new_password):
        # 3. Xóa OTP sau khi dùng xong để bảo mật
        del otp_storage[email]
        return jsonify({'success': True, 'message': 'Đổi mật khẩu thành công! Hãy đăng nhập lại.'})
    else:
        return jsonify({'success': False, 'message': 'Lỗi hệ thống khi cập nhật mật khẩu.'})
if __name__ == "__main__":
    app.run(debug=True)