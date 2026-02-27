from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required
from app.models.order import Order
from app import db

admin_orders_bp = Blueprint(
    "admin_orders",
    __name__,
    url_prefix="/admin/orders"
)


# APPROVE ORDER
@admin_orders_bp.route("/approve/<int:order_id>")
@login_required
def approve_order(order_id):

    order = Order.query.get_or_404(order_id)

    order.status = "to_ship"

    db.session.commit()

    flash("Order approved. Ready to ship.", "success")

    return redirect(url_for("admin.dashboard"))