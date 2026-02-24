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


# ─────────────────────────────
# DASHBOARD
# ─────────────────────────────
@admin_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    logs = WeighLog.query.filter_by(
        status="pending"
    ).order_by(
        WeighLog.created_at.desc()
    ).all()

    return render_template(
        "dashboard/admin.html",
        logs=logs
    )


# ─────────────────────────────
# APPROVE LOG
# ─────────────────────────────
@admin_bp.route("/approve/<int:log_id>")
@login_required
def approve_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    # ❌ STOP if no product name
    if not log.product:
        flash("No product name found in weigh log.", "danger")
        return redirect(url_for("admin.dashboard"))

    # ✅ CREATE PRODUCT
    product = Product(
        name=log.product,
        farmer_id=log.farmer_id,
        stock_quantity=log.weight,
        price=log.suggested_price or 0,
        unit="kg",
        status="approved",
        is_available=True,
        location=log.province or "Unknown",
        image="default_product.jpg"
    )

    db.session.add(product)

    # UPDATE LOG
    log.status = "approved"

    db.session.commit()

    flash("Product approved & posted to buyer!", "success")

    return redirect(url_for("admin.dashboard"))