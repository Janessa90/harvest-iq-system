from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.weigh_logs import WeighLog
from app.models.product import Product
from app.models.order import Order
from app import db


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# ======================================================
# ADMIN DASHBOARD
# ======================================================
@admin_bp.route("/dashboard")
@login_required
def dashboard():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    logs = WeighLog.query.filter(
        WeighLog.status.in_(["pending", "pending_price", "resubmitted"])
    ).order_by(
        WeighLog.created_at.desc()
    ).all()

    pending_orders = Order.query.filter_by(
        status="pending"
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "dashboard/admin.html",
        logs=logs,
        pending_orders=pending_orders
    )


# ======================================================
# APPROVE WEIGH LOG → CREATE PRODUCT
# ======================================================
@admin_bp.route("/approve/<int:log_id>")
@login_required
def approve_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    # ✅ prevent duplicate posting
    if log.status == "approved":
        flash("Already approved.", "info")
        return redirect(url_for("admin.dashboard"))

    product = Product(
        name=log.product,
        farmer_id=log.farmer_id,
        stock_quantity=log.weight or 0,
        price=log.resubmitted_price or log.suggested_price or 0,
        unit="kg",
        status="approved",
        is_available=True,
        location=log.province or "Unknown",
        image="default_product.jpg"
    )

    db.session.add(product)

    log.status = "approved"
    db.session.commit()

    flash("✅ Product approved & posted to marketplace!", "success")
    return redirect(url_for("admin.dashboard"))


# ======================================================
# EDIT PRICE
# ======================================================
@admin_bp.route("/edit-price/<int:log_id>", methods=["POST"])
@login_required
def edit_price(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    try:
        log.resubmitted_price = float(request.form.get("new_price"))
        db.session.commit()
        flash("Price updated.", "success")
    except:
        flash("Invalid price.", "danger")

    return redirect(url_for("admin.dashboard"))


# ======================================================
# REJECT PRICE
# ======================================================
@admin_bp.route("/reject/<int:log_id>", methods=["POST"])
@login_required
def reject_log(log_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    log = WeighLog.query.get_or_404(log_id)

    log.status = "price_rejected"
    log.admin_note = request.form.get("admin_note")

    db.session.commit()

    flash("Price rejected.", "warning")
    return redirect(url_for("admin.dashboard"))


# ======================================================
# VIEW ALL ORDERS
# ======================================================
@admin_bp.route("/orders")
@login_required
def admin_orders():

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    status = request.args.get("status")

    query = Order.query
    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "dashboard/admin_orders.html",
        orders=orders
    )


# ======================================================
# APPROVE ORDER
# pending → to_ship
# ======================================================
@admin_bp.route("/orders/<int:order_id>/approve")
@login_required
def approve_order(order_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)

    if order.status == "pending":
        order.status = "to_ship"
        db.session.commit()
        flash("Order approved.", "success")

    return redirect(url_for("admin.admin_orders"))


# ======================================================
# SHIP ORDER
# to_ship → to_receive
# ======================================================
@admin_bp.route("/orders/<int:order_id>/ship")
@login_required
def ship_order(order_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)

    if order.status == "to_ship":
        order.status = "to_receive"
        db.session.commit()
        flash("Order shipped.", "success")

    return redirect(url_for("admin.admin_orders"))


# ======================================================
# COMPLETE ORDER
# ======================================================
@admin_bp.route("/orders/<int:order_id>/complete")
@login_required
def complete_order(order_id):

    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))

    order = Order.query.get_or_404(order_id)

    if order.status == "to_receive":
        order.status = "completed"
        db.session.commit()
        flash("Order completed.", "success")

    return redirect(url_for("admin.admin_orders"))