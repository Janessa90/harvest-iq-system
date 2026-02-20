from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.product import Product
from app import db

# ✅ Blueprint name MUST be admin_bp
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
        flash("Admin access only.", "danger")
        return redirect(url_for("main.index"))

    # Safe query
    try:
        pending_products = Product.query.filter_by(
            status="pending"
        ).all()
    except:
        pending_products = []

    return render_template(
        "admin/dashboard.html",
        products=pending_products
    )


# ─────────────────────────────
# APPROVE
# ─────────────────────────────
@admin_bp.route("/approve/<int:product_id>")
@login_required
def approve_product(product_id):

    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    product = Product.query.get_or_404(product_id)

    product.status = "approved"
    db.session.commit()

    flash("Product approved.", "success")

    return redirect(url_for("admin.dashboard"))


# ─────────────────────────────
# REJECT
# ─────────────────────────────
@admin_bp.route("/reject/<int:product_id>")
@login_required
def reject_product(product_id):

    if current_user.role != "admin":
        return redirect(url_for("main.index"))

    product = Product.query.get_or_404(product_id)

    product.status = "rejected"
    db.session.commit()

    flash("Product rejected.", "warning")

    return redirect(url_for("admin.dashboard"))
