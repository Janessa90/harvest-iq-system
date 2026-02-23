from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models.product import Product
from sqlalchemy import or_

search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/search"
)

# ─────────────────────────────────────────────
# AI KEYWORD DICTIONARY
# ─────────────────────────────────────────────
AI_KEYWORDS = {
    "tomato": ["kamatis", "toma", "tomat"],
    "potato": ["patatas", "poteto"],

# ─────────────────────────────
# SIMPLE AI KEYWORDS
# ─────────────────────────────
AI_KEYWORDS = {
    "tomato": ["kamatis"],
    "potato": ["patatas"],
    "onion": ["sibuyas"],
    "eggplant": ["talong"],
    "rice": ["bigas", "palay"],
    "corn": ["mais"],
    "banana": ["saging"]
}

 

def expand_keywords(keyword):
    """AI keyword expansion"""

# ─────────────────────────────
# KEYWORD EXPANSION
# ─────────────────────────────
def expand_keywords(keyword):

    keyword = keyword.lower()
    words = [keyword]

    for main, synonyms in AI_KEYWORDS.items():

        if keyword == main or keyword in synonyms:
            words.append(main)
            words.extend(synonyms)

    return list(set(words))


# ─────────────────────────────────────────────
# AI SEARCH ROUTE
# ─────────────────────────────────────────────

# ─────────────────────────────
# SEARCH ROUTE
# ─────────────────────────────
@search_bp.route("/", methods=["GET"])
@login_required
def search():

    keyword = request.args.get("q", "").strip()

    if not keyword:
        products = []

    else:

        expanded = expand_keywords(keyword)

        filters = []

        for word in expanded:
            filters.append(Product.name.ilike(f"%{word}%"))
            filters.append(Product.description.ilike(f"%{word}%"))



            # Partial match
            filters.append(Product.name.ilike(f"%{word}%"))
            filters.append(Product.description.ilike(f"%{word}%"))

            # Autocomplete match
            filters.append(Product.name.ilike(f"{word}%"))

        products = Product.query.filter(
            or_(*filters),
            Product.status == "approved",
            Product.is_available == True
        ).all()

    return render_template(
        "search/results.html",
        products=products,
        keyword=keyword

