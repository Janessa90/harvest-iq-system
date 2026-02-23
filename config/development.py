import os
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────

# config/ folder
basedir = os.path.abspath(os.path.dirname(__file__))

# project root folder
project_root = os.path.dirname(basedir)

# data folder
data_folder = os.path.join(project_root, "data")

# uploads folder
upload_folder = os.path.join(data_folder, "uploads")

# database path
db_path = os.path.join(data_folder, "farmers_marketplace.db")


# ─────────────────────────────────────────────
# DEVELOPMENT CONFIG
# ─────────────────────────────────────────────
class DevelopmentConfig:

    # ─────────────────────────
    # CORE
    # ─────────────────────────
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "harvest-iq-secret-dev-key-2024"
    )

    DEBUG = True

    # ─────────────────────────
    # DATABASE
    # ─────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{db_path}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔥 SQLITE LOCK FIX + SOCKETIO SAFE
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "check_same_thread": False,  # allow multi-thread
            "timeout": 30                # wait before lock error
        }
    }

    # ─────────────────────────
    # MAIL SETTINGS
    # ─────────────────────────
    MAIL_SERVER = os.environ.get(
        "MAIL_SERVER",
        "smtp.gmail.com"
    )

    MAIL_PORT = int(
        os.environ.get("MAIL_PORT", 587)
    )

    MAIL_USE_TLS = True

    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        "noreply@harvestiq.ph"
    )

    # ─────────────────────────
    # UPLOADS
    # ─────────────────────────
    UPLOAD_FOLDER = upload_folder

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # ─────────────────────────
    # STRIPE
    # ─────────────────────────
    STRIPE_PUBLIC_KEY = os.environ.get(
        "STRIPE_PUBLIC_KEY",
        ""
    )

    STRIPE_SECRET_KEY = os.environ.get(
        "STRIPE_SECRET_KEY",
        ""
    )

    # ─────────────────────────
    # PAGINATION
    # ─────────────────────────
    PRODUCTS_PER_PAGE = 12
    ORDERS_PER_PAGE = 10


# ─────────────────────────────────────────────
# AUTO CREATE FOLDERS
# ─────────────────────────────────────────────

os.makedirs(data_folder, exist_ok=True)
os.makedirs(upload_folder, exist_ok=True)

# ─────────────────────────────────────────────
# DEBUG PRINT (optional but helpful)
# ─────────────────────────────────────────────
print("📁 Database Path:", db_path)
print("📁 Upload Folder:", upload_folder)