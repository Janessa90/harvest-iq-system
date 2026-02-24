from flask import Blueprint, request, render_template
from app.models.product import Product
from sqlalchemy import or_

search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/search"
)


@search_bp.route("/")
def search():

    query = request.args.get("q", "").strip()

    if not query:
        return render_template(
            "search/results.html",
            products=[],
            query=query
        )

    # 🔎 SIMPLE AI-LIKE MATCHING
    products = Product.query.filter(
        Product.status == "approved",
        Product.is_available == True,
        or_(
            Product.name.ilike(f"%{query}%"),
            Product.description.ilike(f"%{query}%"),
            Product.location.ilike(f"%{query}%")
        )
    ).all()

    return render_template(
        "search/results.html",
        products=products,
        query=query
    )