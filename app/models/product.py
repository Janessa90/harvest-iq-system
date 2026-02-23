from app import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    # ─────────────────────────────
    # RELATIONSHIPS
    # ─────────────────────────────
    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # OPTIONAL CATEGORY (safe if timbang auto-create)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

    farmer = db.relationship(
        "User",
        backref="products",
        lazy=True
    )

    # ─────────────────────────────
    # BASIC INFO
    # ─────────────────────────────
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False)

    unit = db.Column(
        db.String(50),
        default="kg"
    )

    stock_quantity = db.Column(
        db.Float,   # timbang uses float
        default=0
    )

    min_order_quantity = db.Column(
        db.Float,
        default=1
    )

    # ─────────────────────────────
    # MEDIA
    # ─────────────────────────────
    image = db.Column(
        db.String(255),
        default="default_product.jpg"
    )

    images = db.Column(db.Text)

    # ─────────────────────────────
    # FLAGS
    # ─────────────────────────────
    is_organic = db.Column(
        db.Boolean,
        default=False
    )

    is_available = db.Column(
        db.Boolean,
        default=True
    )

    status = db.Column(
        db.String(20),
        default="approved"
    )

    # ─────────────────────────────
    # HARVEST INFO
    # ─────────────────────────────
    harvest_date = db.Column(db.Date)

    location = db.Column(db.String(200))

    # ─────────────────────────────
    # ANALYTICS
    # ─────────────────────────────
    views = db.Column(db.Integer, default=0)

    # ─────────────────────────────
    # TIMESTAMPS
    # ─────────────────────────────
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # ─────────────────────────────
    # COMPUTED
    # ─────────────────────────────
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    def __repr__(self):
        return f"<Product {self.name}>"