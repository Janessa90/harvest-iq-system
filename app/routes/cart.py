from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.utils.constants import DELIVERY_FEE, FREE_DELIVERY_THRESHOLD, PAYMENT_METHODS

cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/cart"
)

# ─────────────────────────────
# GET CART SESSION
# ─────────────────────────────
def get_cart():
    return session.get("cart", {})


# ─────────────────────────────
# SAVE CART SESSION
# ─────────────────────────────
def save_cart(cart):
    session["cart"] = cart
    session.modified = True


# ─────────────────────────────
# VIEW CART
# ─────────────────────────────
@cart_bp.route("/")
@login_required
def view_cart():

    cart = get_cart()

    items = []
    total = 0

    for product_id, qty in cart.items():

        product = Product.query.get(int(product_id))

        if product and product.is_available:

            subtotal = product.price * qty
            total += subtotal

            items.append({
                "product": product,
                "quantity": qty,
                "subtotal": subtotal
            })

    delivery_fee = 0 if total >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    grand_total = total + delivery_fee

    return render_template(
        "cart/cart.html",
        items=items,
        total=total,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        payment_methods=PAYMENT_METHODS
    )


# ─────────────────────────────
# ADD TO CART ✅ FINAL FIX
# ─────────────────────────────
@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    # ✅ SAFE quantity parsing
    qty_raw = request.form.get("quantity")

    try:
        qty = int(float(qty_raw)) if qty_raw else 1
    except:
        qty = 1

    # ✅ VALIDATION
    if qty <= 0:
        flash("Invalid quantity.", "danger")
        return redirect(url_for(
            "products.product_detail",
            product_id=product_id
        ))

    if product.stock_quantity <= 0:
        flash("Product out of stock.", "danger")
        return redirect(url_for(
            "products.product_detail",
            product_id=product_id
        ))

    qty = min(qty, int(product.stock_quantity))

    cart = get_cart()
    key = str(product_id)

    cart[key] = cart.get(key, 0) + qty

    # prevent overflow
    if cart[key] > product.stock_quantity:
        cart[key] = int(product.stock_quantity)

    save_cart(cart)

    flash(f"{product.name} added to cart!", "success")

    return redirect(url_for("cart.view_cart"))


# ─────────────────────────────
# REMOVE ITEM
# ─────────────────────────────
@cart_bp.route("/remove/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):

    cart = get_cart()

    cart.pop(str(product_id), None)

    save_cart(cart)

    flash("Item removed from cart.", "info")

    return redirect(url_for("cart.view_cart"))


# ─────────────────────────────
# UPDATE CART
# ─────────────────────────────
@cart_bp.route("/update", methods=["POST"])
@login_required
def update_cart():

    cart = get_cart()

    for key, qty in request.form.items():

        if key.startswith("qty_"):

            product_id = key.replace("qty_", "")

            try:
                qty = int(qty)

                product = Product.query.get(int(product_id))

                if product and qty > 0:
                    cart[product_id] = min(qty, product.stock_quantity)

                elif qty <= 0:
                    cart.pop(product_id, None)

            except ValueError:
                pass

    save_cart(cart)

    flash("Cart updated.", "success")

    return redirect(url_for("cart.view_cart"))


# ─────────────────────────────
# CHECKOUT (FIXED)
# ─────────────────────────────
@cart_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():

    cart = get_cart()

    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.view_cart"))

    # 🔥 Get separate address fields
    address = request.form.get("address", "").strip()
    province = request.form.get("province", "").strip()
    city = request.form.get("city", "").strip()
    barangay = request.form.get("barangay", "").strip()

    payment_method = request.form.get("payment_method", "cod")
    notes = request.form.get("notes", "").strip()

    # 🔥 Validate
    if not address or not province or not city or not barangay:
        flash("Please provide a shipping address.", "danger")
        return redirect(url_for("cart.view_cart"))

    # 🔥 Combine into one string
    shipping_address = f"{address}, {barangay}, {city}, {province}"

    items_data = []
    total = 0

    for product_id, qty in cart.items():

        try:
            qty = int(qty)
        except:
            continue

    product = Product.query.get(int(product_id))

    if product and product.is_available and qty > 0:

        subtotal = product.price * qty
        total += subtotal

        items_data.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        })

    delivery_fee = 0 if total >= FREE_DELIVERY_THRESHOLD else DELIVERY_FEE
    grand_total = total + delivery_fee

    order = Order(
        buyer_id=current_user.id,
        total_amount=grand_total,
        delivery_fee=delivery_fee,
        shipping_address=shipping_address,
        payment_method=payment_method,
        notes=notes,
        status="pending",
        payment_status="pending" if payment_method == "cod" else "unpaid",
    )

    db.session.add(order)
    db.session.flush()

    for item in items_data:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            quantity=item["qty"],
            unit_price=item["price"],
            farmer_id=item["product"].farmer_id  # 🔥 IMPORTANT (your model requires this)
        )

        item["product"].stock_quantity -= item["qty"]

        db.session.add(order_item)

    db.session.commit()

    session.pop("cart", None)

    flash(f"Order #{order.id} placed successfully!", "success")

    return redirect(url_for("orders.order_detail", order_id=order.id))