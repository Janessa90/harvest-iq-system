from flask import Blueprint, render_template
from app.models.product import Product
from app.models.category import Category
from app import db

main_bp = Blueprint("main", __name__)

# ==============================
# HOMEPAGE
# ==============================
@main_bp.route("/")
def index():

    # Kunin lahat ng categories
    categories = Category.query.all()

    # Featured products (approved + available only)
    featured = Product.query.filter_by(
        status="approved",
        is_available=True
    ).order_by(Product.views.desc()).limit(8).all()

    return render_template(
        "index.html",
        categories=categories,
        featured=featured
    )
