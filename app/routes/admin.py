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

    print("ADMIN DASHBOARD ACCESS:", current_user.role)

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    logs = WeighLog.query.filter_by(
        status="pending"
    ).order_by(
        WeighLog.created_at.desc()
    ).all()

    print("PENDING LOGS COUNT:", len(logs))

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

    print("APPROVE REQUEST FOR LOG ID:", log_id)

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    print("LOG DATA:", log.product, log.weight, log.suggested_price)

    # ❌ STOP if no product name
    if not log.product:
        flash("No product name found in weigh log.", "danger")
        return redirect(url_for("admin.dashboard"))

    # SAFE VALUES
    stock_value = log.weight or 0
    price_value = log.suggested_price or 0
    location_value = log.province or "Unknown"

    # ✅ CREATE PRODUCT
    product = Product(
        name=log.product,
        farmer_id=log.farmer_id,
        stock_quantity=stock_value,
        price=price_value,
        unit="kg",
        status="approved",
        is_available=True,
        location=location_value,
        image="default_product.jpg"
    )

    db.session.add(product)

    # UPDATE LOG STATUS
    log.status = "approved"

    try:
        db.session.commit()
        print("✅ PRODUCT CREATED SUCCESSFULLY")

        flash("Product approved & posted to buyer!", "success")

    except Exception as e:
        db.session.rollback()
        print("❌ ERROR DURING APPROVAL:", e)
        flash("Error approving product.", "danger")

    return redirect(url_for("admin.dashboard"))