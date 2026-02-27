from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.order import Order, OrderItem

farmer_orders_bp = Blueprint(
    "farmer_orders",
    __name__,
    url_prefix="/farmer/orders"
)


@farmer_orders_bp.route("/")
@login_required
def farmer_orders():

    items = OrderItem.query.filter_by(
        farmer_id=current_user.id
    ).all()

    order_ids = list(set([i.order_id for i in items]))

    orders = Order.query.filter(
        Order.id.in_(order_ids)
    ).all()

    return render_template(
        "farmer/orders.html",
        orders=orders
    )