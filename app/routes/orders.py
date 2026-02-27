from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product

orders_bp = Blueprint('orders', __name__)


# =====================================================
# BUYER — MY ORDERS (WITH STATUS FILTER + COUNTS)
# =====================================================
@orders_bp.route('/')
@login_required
def my_orders():

    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')

    query = Order.query.filter_by(
        buyer_id=current_user.id
    )

    if status:
        query = query.filter_by(status=status)

    orders = query.order_by(
        Order.created_at.desc()
    ).paginate(
        page=page,
        per_page=current_app.config.get('ORDERS_PER_PAGE', 10)
    )

    # STATUS COUNTS (Shopee-style badges)
    counts = {
        "pending": Order.query.filter_by(buyer_id=current_user.id, status="pending").count(),
        "to_ship": Order.query.filter_by(buyer_id=current_user.id, status="to_ship").count(),
        "to_receive": Order.query.filter_by(buyer_id=current_user.id, status="to_receive").count(),
        "completed": Order.query.filter_by(buyer_id=current_user.id, status="completed").count(),
    }

    return render_template(
        'orders/my_orders.html',
        orders=orders,
        counts=counts,
        current_status=status
    )


# =====================================================
# ORDER DETAIL
# =====================================================
@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):

    order = Order.query.get_or_404(order_id)

    if order.buyer_id != current_user.id and current_user.role != "admin":
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))

    return render_template(
        'orders/detail.html',
        order=order
    )


# =====================================================
# CANCEL ORDER (BUYER)
# =====================================================
@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):

    order = Order.query.get_or_404(order_id)

    if order.buyer_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))

    if order.status == 'pending':

        order.status = 'cancelled'

        # Restore stock
        for item in order.items:
            item.product.stock_quantity += item.quantity

        db.session.commit()
        flash('Order cancelled.', 'info')

    else:
        flash('This order cannot be cancelled.', 'danger')

    return redirect(url_for('orders.order_detail', order_id=order.id))


# =====================================================
# BUYER CONFIRM RECEIVED
# to_receive → completed
# =====================================================
@orders_bp.route('/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):

    order = Order.query.get_or_404(order_id)

    if order.buyer_id != current_user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for("main.index"))

    if order.status == "to_receive":
        order.status = "completed"
        db.session.commit()
        flash("Order completed successfully.", "success")

    return redirect(url_for("orders.order_detail", order_id=order.id))


# =====================================================
# FARMER — VIEW ORDERS (VIEW ONLY)
# =====================================================
@orders_bp.route('/farmer/orders')
@login_required
def farmer_orders_view():

    if current_user.role != "farmer":
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.index'))

    farmer_product_ids = [p.id for p in current_user.products]

    if not farmer_product_ids:
        orders = []
    else:
        orders = Order.query.join(OrderItem).filter(
            OrderItem.product_id.in_(farmer_product_ids)
        ).order_by(
            Order.created_at.desc()
        ).all()

    return render_template(
        'orders/farmer_orders.html',
        orders=orders
    )


@orders_bp.route('/farmer/my-products')
@login_required
def farmer_products():

    if current_user.role != "farmer":
        return "Unauthorized"

    return {
        "products": [p.name for p in current_user.products]
    }