from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.weigh_logs import WeighLog
from app.models.product import Product
from app import db

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ─────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────
@admin_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("users.dashboard"))

    logs = WeighLog.query.filter_by(
        status="pending"
    ).all()

    return render_template(
        "dashboard/admin.html",
        logs=logs
    )


# ─────────────────────────────────────────────
# APPROVE WEIGH → AUTO PRICE FROM FARMER
# ─────────────────────────────────────────────
@admin_bp.route("/approve/<int:log_id>")
@login_required
def approve_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("users.dashboard"))

    log = WeighLog.query.get_or_404(log_id)

    # ✅ GET FARMER
    farmer = log.farmer

    # ✅ CREATE PRODUCT AUTO PRICE
    product = Product(
        name=log.product_name,
        farmer_id=log.farmer_id,
        stock_quantity=log.weight_kg,
        price=farmer.price_per_kg,   # AUTO PRICE
        unit="kg",
        status="approved",
        is_available=True,
        location=farmer.province
    )

    db.session.add(product)

    # UPDATE LOG
    log.status = "approved"

    db.session.commit()

    flash("Product approved & posted!", "success")

    return redirect(url_for("admin.dashboard"))