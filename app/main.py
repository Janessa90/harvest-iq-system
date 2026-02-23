from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from datetime import datetime, timezone

# ─────────────────────────────────────────────
# BLUEPRINT
# ─────────────────────────────────────────────
main_bp = Blueprint('main', __name__)

# ─────────────────────────────────────────────
# LANGUAGE SWITCHER
# ─────────────────────────────────────────────
@main_bp.route('/set-lang/<lang>')
def set_language(lang):
    """Switch between English and Tagalog."""
    if lang in ('en', 'tl'):
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))

# ─────────────────────────────────────────────
# CONTEXT PROCESSOR
# ─────────────────────────────────────────────
@main_bp.app_context_processor
def inject_globals():
    return {
        'now': datetime.now(timezone.utc),
    }

# ─────────────────────────────────────────────
# HOMEPAGE
# ─────────────────────────────────────────────
@main_bp.route('/')
def index():
    """Homepage — featured products, categories, top farmers."""

    # Only show approved & available products
    featured = (
        Product.query
        .filter_by(is_available=True, status='approved')
        .order_by(Product.views.desc())
        .limit(8)
        .all()
    )

    categories = Category.query.all()

    # Show approved farmers only
    top_farmers = (
        User.query
        .filter_by(role='farmer', status='approved')
        .limit(6)
        .all()
    )

    return render_template(
        'index.html',
        featured=featured,
        categories=categories,
        top_farmers=top_farmers,
    )

# ─────────────────────────────────────────────
# STATIC PAGES
# ─────────────────────────────────────────────
@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

# ─────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────
@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500