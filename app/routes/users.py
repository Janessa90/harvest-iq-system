from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.order import Order

users_bp = Blueprint("users", __name__)


@users_bp.route("/dashboard")
@login_required
def dashboard():

    print("DASHBOARD ROLE:", current_user.role)

    # Buyer Orders
    orders = Order.query.filter_by(
        buyer_id=current_user.id
    ).all()

    # Products
    products = Product.query.filter_by(
        status="approved",
        is_available=True
    ).order_by(
        Product.created_at.desc()
    ).limit(6).all()

    # ─────────────────────────────
    # ROLE BASED TEMPLATE
    # ─────────────────────────────
    if current_user.role == "farmer":
        print("→ FARMER DASHBOARD")
        return render_template(
            "dashboard/farmer.html",
            orders=orders,
            products=products
        )

    elif current_user.role == "buyer":
        print("→ BUYER DASHBOARD")
        return render_template(
            "dashboard/buyer.html",
            orders=orders,
            products=products
        )

    else:
        print("→ DEFAULT DASHBOARD")
        return render_template(
            "dashboard/buyer.html",
            orders=orders,
            products=products
        )