from app import db


class WeighSession(db.Model):
    _tablename_ = "weigh_sessions"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(db.Integer, nullable=False)

    product_name = db.Column(db.String(255))
    price = db.Column(db.Float)

    is_active = db.Column(
        db.Boolean,
        default=True
    )