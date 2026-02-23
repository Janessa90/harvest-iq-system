from flask import (
    Blueprint, render_template,
    redirect, url_for, flash
)
from flask_login import login_required, current_user

from app.models.weigh_logs import WeighLog
from app.models.product import Product
from app import db


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


# ─────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────
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


# ─────────────────────────────────────
# APPROVE WEIGH LOG
# ─────────────────────────────────────
@admin_bp.route("/approve/<int:log_id>")
@login_required
def approve_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    # ✅ SAFE fallback values
    product_name = log.product or "Unnamed Product"
    price_value = log.suggested_price or 0
    stock_value = log.weight or 0

    # ✅ CREATE PRODUCT FROM LOG
    product = Product(
        name=product_name,          # <-- FIXED
        farmer_id=log.farmer_id,
        stock_quantity=stock_value,
        price=price_value,
        unit="kg",
        status="approved",
        is_available=True,
        location=log.province
    )

    db.session.add(product)

    # ✅ UPDATE LOG STATUS
    log.status = "approved"

    db.session.commit()

    flash("Product approved & posted!", "success")

    return redirect(url_for("admin.dashboard"))