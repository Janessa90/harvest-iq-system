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

    # Pending weigh logs
    logs = WeighLog.query.filter_by(
        status="pending"
    ).all()

    return render_template(
        "dashboard/admin.html",
        logs=logs
    )


# ─────────────────────────────────────────────
# APPROVE WEIGH → CREATE PRODUCT
# ─────────────────────────────────────────────
@admin_bp.route("/approve/<int:log_id>")
@login_required
def approve_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("users.dashboard"))

    log = WeighLog.query.get_or_404(log_id)

    # Create product from weigh log
    product = Product(
        name=log.product_name,
        price=0,  # admin can edit later
        stock_kg=log.weight_kg,
        farmer_id=log.farmer_id,
        status="approved",
        is_available=True
    )

    db.session.add(product)

    # Update log status
    log.status = "approved"

    db.session.commit()

    flash("Product approved & posted!", "success")

    return redirect(url_for("admin.dashboard"))