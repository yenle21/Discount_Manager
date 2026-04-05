/**
 * PROJECT: Discount_Manager
 * AUTHOR: Lê Bảo Yến - Finalized Voucher & UI Logic
 */

// --- 1. THÊM SẢN PHẨM ---
function addToCart(id, name, price, image) {
    fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "id": id, "name": name, "price": price, "image": image })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {
            const badge = document.getElementById('cart-badge');
            if (badge) badge.innerText = data.total_quantity;
            alert("✅ Đã thêm " + name + " vào giỏ hàng!");
        }
    });
}

// --- 2. CẬP NHẬT SỐ LƯỢNG & TÍNH LẠI VOUCHER ---
function updateCartQuantity(productId, delta) {
    fetch('/api/update-cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'id': productId, 'delta': delta })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {
            const badge = document.getElementById('cart-badge');
            if (badge) badge.innerText = data.total_quantity;

            const qtyLabel = document.getElementById('qty-' + productId);
            if (qtyLabel) qtyLabel.innerText = data.new_qty;

            // Tính toán lại Voucher ngay khi tiền hàng thay đổi để tránh tiền âm
            reCalculateVoucher(data.total_amount);

            if (data.new_qty <= 0) {
                const row = document.getElementById('product-row-' + productId);
                if (row) row.remove();
                if (data.total_quantity === 0) location.reload();
            }
        }
    });
}

function reCalculateVoucher(newSubtotal) {
    fetch('/api/apply-voucher', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "code": "RE_CALCULATE", "total_amount": newSubtotal })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {
            const discountEl = document.getElementById('discount-val');
            if (discountEl) discountEl.innerText = "-" + data.total_discount.toLocaleString('vi-VN') + "đ";
            renderVoucherTags(data.applied_details);
            updatePriceUI(newSubtotal, data.new_total);
        } else {
            document.getElementById('discount-val').innerText = "0đ";
            const tagContainer = document.getElementById('applied-vouchers-container');
            if (tagContainer) tagContainer.innerHTML = "";
            updatePriceUI(newSubtotal, newSubtotal);
        }
    });
}

function updatePriceUI(subtotal, finalTotal) {
    const tamTinhEl = document.getElementById('tam-tinh-val');
    if (tamTinhEl) tamTinhEl.innerText = subtotal.toLocaleString('vi-VN') + 'đ';

    const summarySubtotal = document.getElementById('summary-subtotal');
    if (summarySubtotal) summarySubtotal.innerText = subtotal.toLocaleString('vi-VN') + 'đ';

    const totals = document.querySelectorAll('.js-total-amount');
    totals.forEach(el => {
        el.innerText = finalTotal.toLocaleString('vi-VN') + 'đ';
    });
}

// --- 3. QUẢN LÝ VOUCHER & UI ---
function renderVoucherTags(appliedDetails) {
    const container = document.getElementById('applied-vouchers-container');
    const clearBtn = document.getElementById('btn-clear-vouchers');
    if (!container) return;

    let html = "";
    let hasVoucher = false;

    if (appliedDetails && appliedDetails.SHIPPING) {
        html += `<div class="applied-voucher-tag tag-ship">🚚 ${appliedDetails.SHIPPING.code} (Giảm ${appliedDetails.SHIPPING.discount_amount.toLocaleString()}đ)</div>`;
        hasVoucher = true;
    }
    if (appliedDetails && appliedDetails.PROMOTION) {
        html += `<div class="applied-voucher-tag tag-promo">🏷️ ${appliedDetails.PROMOTION.code} (Giảm ${appliedDetails.PROMOTION.discount_amount.toLocaleString()}đ)</div>`;
        hasVoucher = true;
    }

    container.innerHTML = html;
    if (clearBtn) clearBtn.style.display = hasVoucher ? "block" : "none";
}

function loadVoucherList() {
    const totalElement = document.querySelector(".js-total-amount");
    if (!totalElement) return;

    const currentTotal = parseFloat(totalElement.innerText.replace(/[^0-9]/g, ''));
    const categoriesInCart = Array.from(document.querySelectorAll('[id^="product-row-"]'))
                                  .map(row => row.getAttribute('data-category-id'));

    fetch('/api/vouchers')
        .then(res => res.json())
        .then(vouchers => {
            const container = document.getElementById('voucher-list-container');
            if (!container) return;
            container.innerHTML = '';

            vouchers.forEach(v => {
                const now = new Date();
                const expiryDate = v.expiry !== "Không hết hạn" ? parseDate(v.expiry) : null;

                const isExpired = expiryDate && expiryDate < now;
                const isAmountValid = currentTotal >= v.condition;
                let isCategoryValid = true;
                if (v.category_id && v.category_id.toString() !== "None") {
                    isCategoryValid = categoriesInCart.includes(v.category_id.toString());
                }

                const isLocked = isExpired || !isAmountValid || !isCategoryValid;

                const card = document.createElement('div');
                // Thêm class voucher-locked để làm mờ mã không dùng được
                card.className = `voucher-item-card p-3 border rounded mb-3 ${isLocked ? 'voucher-locked' : 'border-primary shadow-sm'}`;

                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center w-100">
                        <div class="voucher-info flex-grow-1 pe-3">
                            <div class="d-flex align-items-center mb-1">
                                <span class="badge ${v.type === 'Vận chuyển' ? 'bg-info' : 'bg-warning text-dark'} me-2">
                                    ${v.type || 'Giảm giá'}
                                </span>
                                <h6 class="fw-bold mb-0">${v.code}</h6>
                            </div>

                            ${isExpired ? `<small class="text-danger d-block fw-bold">❌ Mã hết hạn</small>`
                              : (!isCategoryValid ? `<small class="text-danger d-block fw-bold">⚠️ Không đúng danh mục</small>`
                              : (!isAmountValid ? `<small class="text-danger d-block fw-bold">⚠️ Thiếu ${(v.condition - currentTotal).toLocaleString()}đ</small>`
                              : `<small class="text-success d-block fw-bold">✅ Được sử dụng</small>`))}

                            <p class="mb-1 mt-1 text-muted small" style="line-height: 1.3;">
                                <i class="fa-solid fa-circle-info me-1"></i> ${v.description || 'Giảm giá cực sốc dành cho bạn.'}
                            </p>

                            <small class="text-muted" style="font-size: 0.72rem;">HSD: ${v.expiry}</small>
                        </div>

                        <div class="voucher-action text-end" style="min-width: 80px;">
                            ${!isLocked ? `
                                <button class="btn btn-primary btn-sm px-3 rounded-pill fw-bold"
                                        onclick="selectVoucher('${v.code}')">Chọn</button>
                            ` : `
                                <button class="btn btn-secondary btn-sm px-3 rounded-pill fw-bold" disabled>Khóa</button>
                            `}
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        });
}

function selectVoucher(code) {
    const vInput = document.getElementById('voucher-code');
    if (vInput) { vInput.value = code; applyVoucher(); }
}

function applyVoucher() {
    const vInput = document.getElementById("voucher-code");
    if (!vInput || !vInput.value.trim()) return;
    const subtotalText = document.getElementById("summary-subtotal").innerText;
    const currentSubtotal = parseFloat(subtotalText.replace(/[^0-9]/g, '')) || 0;

    fetch('/api/apply-voucher', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "code": vInput.value.trim(), "total_amount": currentSubtotal })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 200) {
            alert("🎉 " + data.message);
            document.getElementById('discount-val').innerText = "-" + data.total_discount.toLocaleString('vi-VN') + "đ";
            renderVoucherTags(data.applied_details);
            updatePriceUI(currentSubtotal, data.new_total);
            vInput.value = "";
            loadVoucherList();
        } else { alert("❌ " + data.message); }
    });
}

function clearAllVouchers(event) {
    if (event) event.stopPropagation();
    if (!confirm("Yến muốn gỡ tất cả mã giảm giá?")) return;

    document.getElementById('applied-vouchers-container').innerHTML = "";
    document.getElementById('discount-val').innerText = "0đ";
    document.getElementById('btn-clear-vouchers').style.display = "none";

    const subtotal = parseFloat(document.getElementById("summary-subtotal").innerText.replace(/[^0-9]/g, ''));
    updatePriceUI(subtotal, subtotal);

    fetch('/api/clear-vouchers', { method: 'POST' });
}

// --- 4. THANH TOÁN ---
function processCheckout() {
    if (typeof IS_AUTHENTICATED !== 'undefined' && !IS_AUTHENTICATED) {
        if (confirm("Yến ơi, bạn cần đăng nhập để thanh toán?")) window.location.href = "/login";
        return;
    }
    const name = document.getElementById("receiver-name").value.trim();
    const phone = document.getElementById("receiver-phone").value.trim();
    const address = document.getElementById("receiver-address").value.trim();
    const paymentMethod = document.getElementById("payment-method").value;

    const nameRegex = /^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰYỲỴÝỶỸửữựyỳỵýỷỹ\s]{2,50}$/;
    if (!nameRegex.test(name)) { alert("⚠️ Tên không hợp lệ."); return; }
    if (!/^(03|05|07|08|09)\d{8}$/.test(phone)) { alert("⚠️ SĐT không đúng."); return; }
    if (address.length < 10) { alert("⚠️ Địa chỉ quá ngắn."); return; }

    if (confirm("Xác nhận đặt hàng?")) {
        fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, address, "payment_method": paymentMethod })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 200) {
                alert("🚀 Đặt hàng thành công!");
                window.location.href = "/";
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const dModal = document.getElementById('discountModal');
    if (dModal) dModal.addEventListener('show.bs.modal', loadVoucherList);
});

function parseDate(str) {
    const p = str.split('/');
    return new Date(p[2], p[1] - 1, p[0]);
}