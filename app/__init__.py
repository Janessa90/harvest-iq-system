from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_migrate import Migrate
from sqlalchemy import text

from config.development import DevelopmentConfig


# ─────────────────────────────────────────────
# EXTENSIONS
# ─────────────────────────────────────────────
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

socketio = SocketIO(
    async_mode="threading",
    logger=True,
    engineio_logger=True
)

migrate = Migrate()


# ─────────────────────────────────────────────
# APP FACTORY
# ─────────────────────────────────────────────
def create_app(config=DevelopmentConfig):

    flask_app = Flask(__name__)
    flask_app.config.from_object(config)
    flask_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "timeout": 30
    }
}

    # ===============================
    # INIT EXTENSIONS
    # ===============================
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    bcrypt.init_app(flask_app)
    mail.init_app(flask_app)
    socketio.init_app(flask_app, cors_allowed_origins="*")

    # ===============================
    # SQLITE WAL MODE
    # ===============================
    with flask_app.app_context():
        db.session.execute(text("PRAGMA journal_mode=WAL;"))
        db.session.commit()

    # ===============================
    # LOGIN SETTINGS
    # ===============================
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # ===============================
    # USER LOADER
    # ===============================
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ===============================
    # REGISTER BLUEPRINTS ✅
    # ===============================
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
    from app.routes.device import device_bp
    from app.routes.farmer_orders import farmer_orders_bp

    flask_app.register_blueprint(auth_bp, url_prefix="/auth")
    flask_app.register_blueprint(products_bp, url_prefix="/products")
    flask_app.register_blueprint(orders_bp, url_prefix="/orders")
    flask_app.register_blueprint(users_bp, url_prefix="/users")
    flask_app.register_blueprint(admin_bp, url_prefix="/admin")
    flask_app.register_blueprint(search_bp, url_prefix="/search")
    flask_app.register_blueprint(cart_bp, url_prefix="/cart")
    flask_app.register_blueprint(payment_bp, url_prefix="/payment")
    flask_app.register_blueprint(main_bp)

    # ✅ APIs
    flask_app.register_blueprint(api_bp)
    flask_app.register_blueprint(device_bp)

    flask_app.register_blueprint(farmer_orders_bp)

    # ===============================
    # LOAD MODELS
    # ===============================
    with flask_app.app_context():

        from app.models.product import Product
        from app.models.order import Order, OrderItem
        from app.models.weigh_logs import WeighLog
        from app.models.device import Device
        from app.models.weigh_session import WeighSession

        try:
            from app.models.category import Category
        except Exception:
            pass

        db.create_all()

        from app.utils.helpers import seed_categories, seed_admin
        seed_categories()
        seed_admin()

    return flask_app