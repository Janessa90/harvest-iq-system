from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from app import db
from app.models.user import User   # ✅ IMPORTANT FIX
from app.models.product import Product
from app.models.order import Order

try:
    from app.models.device import Device
except Exception:
    Device = None


users_bp = Blueprint("users", __name__)


# ============================================================
# DASHBOARD
# ============================================================
@users_bp.route("/dashboard")
@login_required
def dashboard():

    orders = Order.query.filter_by(
        buyer_id=current_user.id
    ).order_by(Order.created_at.desc()).all()

    products = Product.query.filter_by(
        status="approved",
        is_available=True
    ).order_by(Product.created_at.desc()).limit(6).all()

    farmer_products = []
    total_revenue = 0

    if current_user.role == "farmer":

        farmer_products = Product.query.filter_by(
            farmer_id=current_user.id
        ).all()

        for p in farmer_products:
            total_revenue += (p.stock_quantity or 0) * (p.price or 0)

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
# START WEIGH
# ============================================================
@users_bp.route("/start-weigh", methods=["POST"])
@login_required
def start_weigh():

    if current_user.role != "farmer":
        flash("Unauthorized.", "danger")
        return redirect(url_for("users.dashboard"))

    session["active_farmer_id"] = current_user.id

    if Device:
        device = Device.query.get(1)  # ✅ YOUR REAL DEVICE
        if device:
            device.weighing = True
            device.current_farmer_id = current_user.id
            db.session.commit()

    flash("Weighing started.", "success")
    return redirect(url_for("users.dashboard"))


# ============================================================
# STOP WEIGH
# ============================================================
@users_bp.route("/stop-weigh", methods=["POST"])
@login_required
def stop_weigh():

    session.pop("active_farmer_id", None)

    if Device:
        device = Device.query.get(1)
        if device:
            device.weighing = False
            device.current_farmer_id = None
            db.session.commit()

    flash("Weighing stopped.", "warning")
    return redirect(url_for("users.dashboard"))


# ============================================================
# ✅ REGISTER (FULL FIX)
# ============================================================
@users_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        role = request.form.get("role", "buyer")

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        full_name = request.form.get("full_name")
        phone = request.form.get("phone")

        province = request.form.get("province")
        city = request.form.get("city")
        barangay = request.form.get("barangay")
        full_address = request.form.get("full_address")

        # ✅ ROLE VALIDATION
        if role == "farmer" and not username:
            flash("Username required for farmer.", "danger")
            return redirect(url_for("users.register"))

        if role == "buyer" and not email:
            flash("Email required for buyer.", "danger")
            return redirect(url_for("users.register"))

        if not password:
            flash("Password required.", "danger")
            return redirect(url_for("users.register"))

        # ✅ CHECK EXISTING USER
        existing = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing:
            flash("User already exists.", "warning")
            return redirect(url_for("users.register"))

        # ✅ CREATE USER
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            province=province,
            city=city,
            barangay=barangay,
            full_address=full_address,
            role=role,
            status="approved" if role == "buyer" else "pending"
        )

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")