from flask import Blueprint, request, jsonify
from app.models.product import Product

search_bp = Blueprint("search", __name__)

@search_bp.route("/api/search-products")
def search_products():

    query = request.args.get("q", "")

    products = Product.query.filter(
        Product.name.ilike(f"%{query}%")
    ).all()

    results = []

    for p in products:

        farmer = p.farmer

        location = "Unknown"

        if farmer:
            location = f"{farmer.barangay or ''}, {farmer.city or ''}, {farmer.province or ''}"

        results.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock_quantity,
            "farmer": farmer.full_name if farmer else "Unknown",
            "location": location,
            "image": p.image
        })

    return jsonify(results)