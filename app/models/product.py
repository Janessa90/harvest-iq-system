from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    
    # These strings MUST match the __tablename__ in other files
    farmer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    
    # Relationships using strings avoid circular import crashes
    farmer = db.relationship("User", backref="products")
    category_rel = db.relationship("Category", backref="products")

    def __repr__(self):
        return f"<Product {self.name}>"