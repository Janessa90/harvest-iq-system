from app import db
from datetime import datetime


# ─────────────────────────────────────────────
# ORDER MODEL
# ─────────────────────────────────────────────
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    # BUYER
    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    buyer = db.relationship(
        "User",
        backref="orders",
        lazy=True
    )

    # STATUS FLOW
    status = db.Column(
        db.String(30),
        default="pending"
    )
    """
    pending     = waiting admin confirmation
    to_ship     = approved by admin
    to_receive  = shipped by farmer
    completed   = received by buyer
    cancelled   = cancelled
    """

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    delivery_fee = db.Column(
        db.Float,
        default=0
    )

    shipping_address = db.Column(
        db.Text,
        nullable=False
    )

    payment_method = db.Column(
        db.String(50),
        default="cod"
    )

    payment_status = db.Column(
        db.String(30),
        default="unpaid"
    )

    payment_reference = db.Column(
        db.String(200)
    )

    notes = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # RELATIONSHIP
    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)

    @property
    def grand_total(self):
        return self.total_amount + (self.delivery_fee or 0)

    def __repr__(self):
        return f"<Order #{self.id} - {self.status}>"


# ─────────────────────────────────────────────
# ORDER ITEMS
# ─────────────────────────────────────────────
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    # VERY IMPORTANT → Farmer view
    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Float,
        nullable=False
    )

    product = db.relationship(
        "Product",
        backref="order_items",
        lazy=True
    )

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return f"<OrderItem Order:{self.order_id} Product:{self.product_id}>"