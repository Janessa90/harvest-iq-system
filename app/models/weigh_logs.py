from app import db
from datetime import datetime


class WeighLog(db.Model):
    _tablename_ = "weigh_logs"

    id = db.Column(db.Integer, primary_key=True)

    # ✅ FIXED FOREIGN KEY
    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),   # MUST MATCH _tablename_
        nullable=False
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

    # ✅ RELATIONSHIP
    farmer = db.relationship(
        "User",
        backref="weigh_logs"
    )