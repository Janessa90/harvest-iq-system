from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate
from datetime import datetime
import sys
import os
sys.path.append(os.getcwd()) # Adds the current folder to Python's search path

from config.development import DevelopmentConfig

# ... (rest of the extensions)

# ─────────────────────────────────────────────
# INIT EXTENSIONS
# ─────────────────────────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
socketio = SocketIO(async_mode="threading")
migrate = Migrate()

# ─────────────────────────────────────────────
# APP FACTORY
# ─────────────────────────────────────────────
def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    # INIT EXTENSIONS
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # LOGIN CONFIG
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # USER LOADER
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        # Use session.get for SQLAlchemy 2.0 compatibility
        return db.session.get(User, int(user_id))

    # REGISTER BLUEPRINTS
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.users import users_bp
    from app.routes.admin import admin_bp
    from app.routes.search import search_bp
    from app.routes.cart import cart_bp
    from app.routes.payment import payment_bp
    from app.routes.main import main_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(payment_bp, url_prefix="/payment")
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # CONTEXT PROCESSOR
    @app.context_processor
    def inject_globals():
        lang = session.get("lang", "en")
        return {
            "lang": lang,
            "now": datetime.now(),
            "unread_count": 0
        }

    # 🚀 FORCE MODEL REGISTRATION (CRITICAL)
    with app.app_context():
        # Step A: Import the User model first and ALONE
        from app.models.user import User
        
        # Step B: Manually tell the DB to register the User metadata
        db.get_engine(app=app) 
        
        # Step C: Import everything else
        from app.models.category import Category
        from app.models.product import Product
        from app.models.order import Order
        from app.models.weigh_logs import WeighLog
        from app.models.review import Review

        # Step D: Create tables
        db.create_all()

        # Step E: Seeders
        from app.utils.helpers import seed_categories, seed_admin
        try:
            seed_categories()
            seed_admin()
        except Exception as e:
            print(f"Seeding skipped: {e}")

    return app