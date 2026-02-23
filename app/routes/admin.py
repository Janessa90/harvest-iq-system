<<<<<<< HEAD
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
=======
from flask import (
    Blueprint, render_template,
    redirect, url_for, flash
)
from flask_login import login_required, current_user

>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
from app.models.weigh_logs import WeighLog
from app.models.product import Product
from app import db

<<<<<<< HEAD
=======

>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


<<<<<<< HEAD
# ─────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────
=======
# ─────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────
>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
@admin_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
<<<<<<< HEAD
        return redirect(url_for("users.dashboard"))

    logs = WeighLog.query.filter_by(
        status="pending"
=======
        return redirect(url_for("main.index"))

    logs = WeighLog.query.filter_by(
        status="pending"
    ).order_by(
        WeighLog.created_at.desc()
>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
    ).all()

    return render_template(
        "dashboard/admin.html",
        logs=logs
    )


<<<<<<< HEAD
# ─────────────────────────────────────────────
# APPROVE WEIGH → AUTO PRICE FROM FARMER
# ─────────────────────────────────────────────
=======
# ─────────────────────────────────────
# APPROVE WEIGH LOG
# ─────────────────────────────────────
>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
@admin_bp.route("/approve/<int:log_id>")
@login_required
def approve_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
<<<<<<< HEAD
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
=======
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    # ✅ CREATE PRODUCT FROM LOG
    product = Product(
        name=log.product,
        farmer_id=log.farmer_id,
        stock_quantity=log.weight,
        price=log.suggested_price,
        unit="kg",
        status="approved",
        is_available=True,
        location=log.province
>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
    )

    db.session.add(product)

<<<<<<< HEAD
    # UPDATE LOG
=======
    # ✅ UPDATE LOG STATUS
>>>>>>> 24211ea (Updated AI search, weighing system, admin approval, dashboards)
    log.status = "approved"

    db.session.commit()

    flash("Product approved & posted!", "success")

    return redirect(url_for("admin.dashboard"))