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
from discounts import app, db, login, dao, utils
from discounts.decorators import admin_required
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


#---------------- TRANG ADMIN ------------------------
@app.route("/create")
@admin_required
def create():
    categories = dao.load_categories()
    return render_template("admin/create_voucher.html", categories=categories)

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
        if v.Hinhthuc:
            hinh_thuc_list.add(v.Hinhthuc)
        now = datetime.now()
        if v.TrangThai == 'Inactive':
            display_status = "pending"  # Do người dùng chủ động tắt
        elif v.NgayKT and now > v.NgayKT:
            display_status = "expired"  # Hết hạn theo thời gian
        elif v.DaSuDung >= v.SoLuong:
            display_status = "expired"
        elif v.NgayBD and now < v.NgayBD:
            display_status = "pending"
        else:
            display_status = "active"
        v.display_status = display_status
        # 3. Bộ lọc Search
        if kw and kw.lower() not in (v.MaGG or "").lower() and kw.lower() not in (v.MoTa or "").lower():
            continue
        # 4. Bộ lọc theo Trạng thái
        if trang_thai and display_status != trang_thai:
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
# Thêm voucher
@app.route('/add', methods=['POST'])
@admin_required
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

        if ngay_kt <= ngay_bd:
            flash("Ngày kết thúc phải lớn hơn ngày bắt đầu!", "danger")
            return redirect('/create')

        if ngay_kt < datetime.now():
            flash("Ngày kết thúc không được ở quá khứ!", "danger")
            return redirect('/create')

        data = {
            "MaGG": MaGG,
            "Hinhthuc": request.form.get('Hinhthuc'),
            "LoaiGG": request.form.get('LoaiGG'),
            "GiaTri": float(request.form.get('GiaTri') or 0),
            "SoLuong": int(request.form.get('SoLuong') or 1),
            "NgayBD": ngay_bd,
            "NgayKT": ngay_kt,
            "TrangThai": "Active" if request.form.get('TrangThai') == "active" else "Inactive",
            "MoTa": request.form.get('MoTa'),
            "admin_id": current_user.id,
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
# edit voucher
# Route 1: Mở trang sửa (đổ dữ liệu vào create.html)
@app.route('/edit/<string:ma_gg>')
def edit_voucher_view(ma_gg):
    v_edit = dao.get_voucher_by_id(ma_gg)
    categories = dao.load_categories()
    if v_edit:
        return render_template('admin/create_voucher.html', v_edit=v_edit,c=categories)
    flash("Không tìm thấy mã giảm giá!", "danger")
    return redirect('/admin')


# update voucher
@app.route('/update/<string:ma_gg>', methods=['POST'])
def update_voucher_route(ma_gg):
    try:
        ngay_bd = request.form.get('NgayBD')
        ngay_kt = request.form.get('NgayKT')

        if ngay_kt <= ngay_bd:
            flash("Ngày kết thúc phải lớn hơn ngày bắt đầu!", "danger")
            return redirect('/create')

        if ngay_kt < datetime.now():
            flash("Ngày kết thúc không được ở quá khứ!", "danger")
            return redirect('/create')

        data = {
            "Hinhthuc": request.form.get('Hinhthuc'),
            "LoaiGG": request.form.get('LoaiGG'),
            "GiaTri": float(request.form.get('GiaTri') or 0),
            "SoLuong": int(request.form.get('SoLuong') or 0),
            "NgayBD": datetime.strptime(ngay_bd, "%Y-%m-%dT%H:%M") if ngay_bd else None,
            "NgayKT": datetime.strptime(ngay_kt, "%Y-%m-%dT%H:%M") if ngay_kt else None,
            "TrangThai": "Active" if request.form.get('TrangThai') == "active" else "Inactive",
            "MoTa": request.form.get('MoTa'),
            "DieuKien": float(request.form.get('DieuKien') or 0),
            "DieuKienSP": request.form.get('DieuKienSP')
        }

        if dao.update_voucher(ma_gg, data):
            flash(f"Cập nhật mã {ma_gg} thành công!", "success")
        else:
            flash("Có lỗi xảy ra khi lưu dữ liệu!", "danger")

        return redirect('/admin')
    except Exception as e:
        flash(f"Lỗi: {str(e)}", "danger")
        return redirect('/admin')
# xóa mã gg
@app.route('/delete/<maGG>', methods=['POST'])
@login_required
def delete_voucher(maGG):
    if int(current_user.user_role) != UserRole.ADMIN:
        return jsonify({"status": 403, "message": "Không có quyền!"})

    try:
        voucher = dao.get_voucher_by_id(maGG)
        if not voucher:
            flash("Voucher không tồn tại!", "danger")
            return redirect('/admin')

        # không cho xóa nếu người dùng đã dùng voucher
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
    key = app.config['CART_KEY'] #cart
    cart = session.get(key)

    if cart and product_id in cart:
        cart[product_id]['quantity'] = int(request.json['quantity'])

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
                "status": 400,
                "message": f"Đơn hàng phải tối thiểu {price} VNĐ mới dùng được!"
            })
        # so sánh danh mục có khớp với điều kiện sp danh mục ko
        if v.DieuKienSP and str(v.DieuKienSP).strip() != "" and str(v.DieuKienSP) != "None":
            # Lấy tất cả id danh mục đang có trong giỏ hàng
            categories_in_cart = [str(item.get('category_id')) for item in cart.values()]
            # Nếu danh mục Voucher không nằm trong danh sách cate
            if str(v.DieuKienSP) not in categories_in_cart:
                return jsonify({
                    "status": 400,
                    "message": f"Mã này chỉ áp dụng cho sản phẩm thuộc danh mục: {v.DieuKienSP}!"
                })

        now = datetime.now()

        #  kiểm tra ngày bắt đầu
        if v.NgayBD and now < v.NgayBD:
            start_date = v.NgayBD.strftime('%d/%m/%Y %H:%M')
            return jsonify({
                "status": 400,
                "message": f"Mã này chưa đến hạn sử dụng. Vui lòng quay lại vào lúc {start_date} nhé!"
            })

        # kiểm tra ngày kết thúc
        if v.NgayKT and now > v.NgayKT:
            return jsonify({
                "status": 400,
                "message": "Mã giảm giá này đã hết hạn sử dụng rồi!"
            })
        # kiếm tra số lượng voucher hiện tại so với lượt đã sử dụng
        if v.SoLuong is not None and v.SoLuong > 0:
            if v.DaSuDung >= v.SoLuong:
                return jsonify({
                    "status": 400,
                    "message": "Rất tiếc, mã này hết lượt sử dụng rồi!"
                })
        # kiếm tra hết điều kiện rồi thì mới đc apply
        applied_vouchers = session.get('applied_vouchers', {})
        kind = 'SHIPPING' if 'shipping' in v.Hinhthuc.lower() else 'PROMOTION'
        #kiểm tra mã tối đa đc dùng ở 2 loại
        if kind not in applied_vouchers and len(applied_vouchers) >= 2:
            return jsonify({"status": 400, "message": "Mỗi đơn hàng chỉ được áp dụng tối đa 2 mã!"})

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
        return jsonify({"status": 400, "message": "Giỏ hàng trống!"})

    data = request.json
    ten_nguoi_nhan = data.get('name')
    sdt = data.get('phone')
    dia_chi = data.get('address')
    hinh_thuc_tt = data.get('payment_method', 'Tiền mặt')

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
        # Chỉ lấy những mã chưa hết hạn ngày kết thúc
        if not v.NgayKT or now <= v.NgayKT:
            # Tính số lượng còn lại (đảm bảo không bị âm)
            v.con_lai = max(0, v.SoLuong-v.DaSuDung)
            # Biến kiểm tra xem còn lượt dùng hay không
            v.is_available = v.con_lai > 0

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
            "message": "Thông tin không khớp! Kiểm tra lại Username hoặc Email"
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