from app import db
from datetime import datetime


class WeighLog(db.Model):
    __tablename__ = "weigh_logs"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    product_name = db.Column(db.String(100))

    weight_kg = db.Column(db.Float)

    status = db.Column(
        db.String(20),
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    farmer = db.relationship(
        "User",
        backref="weigh_logs"
    )