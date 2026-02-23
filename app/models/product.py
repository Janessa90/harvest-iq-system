from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    # FOREIGN KEYS
    # Correctly references the 'users' table name we set in user.py
    farmer_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"), 
        nullable=False
    )

    # Ensure the 'categories' table exists before create_all is called
    category_id = db.Column(
        db.Integer, 
        db.ForeignKey("categories.id"), 
        nullable=False
    )

    # ─────────────────────────────
    # Basic Info
    # ─────────────────────────────
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), default="kg")
    
    stock_quantity = db.Column(
        db.Integer, 
        nullable=False, 
        default=0
    )
    
    min_order_quantity = db.Column(
        db.Integer, 
        default=1
    )

    # ─────────────────────────────
    # Images
    # ─────────────────────────────
    image = db.Column(
        db.String(255), 
        default="default_product.jpg"
    )
    images = db.Column(db.Text) # Can store JSON strings of multiple image paths

    # ─────────────────────────────
    # Product Tags
    # ─────────────────────────────
    is_organic = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)

    # ─────────────────────────────
    # Admin Approval Status
    # ─────────────────────────────
    status = db.Column(
        db.String(20), 
        default="pending"
    )

    # ─────────────────────────────
    # Harvest Info
    # ─────────────────────────────
    harvest_date = db.Column(db.Date)
    location = db.Column(db.String(200))

    # ─────────────────────────────
    # Analytics
    # ─────────────────────────────
    views = db.Column(db.Integer, default=0)

    # ─────────────────────────────
    # Timestamps
    # ─────────────────────────────
    created_at = db.Column(
        db.DateTime, 
        default=db.func.now() # Best practice for DB-level timestamps
    )

    updated_at = db.Column(
        db.DateTime, 
        default=db.func.now(), 
        onupdate=db.func.now()
    )

    # ─────────────────────────────
    # Relationships
    # ─────────────────────────────
    # Backref "product" allows access via review.product
    reviews = db.relationship(
        "Review", 
        backref="product", 
        lazy=True, 
        cascade="all, delete-orphan"
    )

    order_items = db.relationship(
        "OrderItem", 
        backref="product", 
        lazy=True
    )

    # Explicit relationship back to the Farmer (User)
    farmer = db.relationship(
        "User", 
        backref="products", 
        lazy=True
    )

    # ─────────────────────────────
    # Computed Properties
    # ─────────────────────────────
    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0 and self.is_available

    def __repr__(self):
        return f"<Product {self.name}>"