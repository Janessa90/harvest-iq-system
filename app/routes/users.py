from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.order import Order
from app import db

# try import device model safely
try:
    from app.models.device import Device
except Exception:
    Device = None

users_bp = Blueprint("users", __name__)


# ============================================================
# 🧭 USER DASHBOARD
# ============================================================
@users_bp.route("/dashboard")
@login_required
def dashboard():

    print("DASHBOARD ROLE:", current_user.role)

    # ─────────────────────────────
    # BUYER ORDERS
    # ─────────────────────────────
    orders = Order.query.filter_by(
        buyer_id=current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    # ─────────────────────────────
    # APPROVED PRODUCTS (BUYER VIEW)
    # ─────────────────────────────
    products = Product.query.filter_by(
        status="approved",
        is_available=True
    ).order_by(
        Product.created_at.desc()
    ).limit(6).all()

    print("AVAILABLE PRODUCTS COUNT:", len(products))

    # ─────────────────────────────
    # FARMER OWN PRODUCTS
    # ─────────────────────────────
    farmer_products = []
    total_revenue = 0

    if current_user.role == "farmer":

        farmer_products = Product.query.filter_by(
            farmer_id=current_user.id
        ).order_by(
            Product.created_at.desc()
        ).all()

        print("FARMER PRODUCTS COUNT:", len(farmer_products))

        for p in farmer_products:
            if p.stock_quantity and p.price:
                total_revenue += p.stock_quantity * p.price

    # ─────────────────────────────
    # ROLE-BASED TEMPLATE
    # ─────────────────────────────
    if current_user.role == "farmer":
        return render_template(
            "dashboard/farmer.html",
            orders=orders,
            products=products,
            farmer_products=farmer_products,
            total_revenue=total_revenue
        )

    return render_template(
        "dashboard/buyer.html",
        orders=orders,
        products=products
    )


# ============================================================
# 🚀 START WEIGH (MULTI-FARMER SAFE)
# ============================================================
@users_bp.route("/start-weigh", methods=["POST"])
@login_required
def start_weigh():

    if current_user.role != "farmer":
        flash("Unauthorized.", "danger")
        return redirect(url_for("users.dashboard"))

    print(f"🔥 START requested by farmer {current_user.id}")

    # ✅ remember which farmer initiated weighing
    session["active_farmer_id"] = current_user.id
    print("ACTIVE FARMER SET:", session["active_farmer_id"])

    # ✅ trigger the SINGLE physical scale (device id = 3)
    if Device:
        device = Device.query.get(3)
        if device:
            device.weighing = True
            db.session.commit()
            print("✅ Device weighing set to TRUE")
        else:
            print("❌ Device ID 3 not found")
    else:
        print("⚠️ Device model missing — skipping device trigger")

    flash("Start command sent to weighing hardware.", "success")
    return redirect(url_for("users.dashboard"))


# ============================================================
# 🛑 STOP WEIGH (optional but recommended)
# ============================================================
@users_bp.route("/stop-weigh", methods=["POST"])
@login_required
def stop_weigh():

    if Device:
        device = Device.query.get(3)
        if device:
            device.weighing = False
            db.session.commit()
            print("🛑 Device weighing set to FALSE")

    flash("Weighing stopped.", "warning")
    return redirect(url_for("users.dashboard"))