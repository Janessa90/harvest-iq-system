from app import db
from datetime import datetime


class WeighLog(db.Model):
    _tablename_ = "weigh_logs"

    id = db.Column(db.Integer, primary_key=True)

    # FARMER INFO
    farmer_id = db.Column(db.Integer)
    farmer_name = db.Column(db.String(150))
    phone = db.Column(db.String(50))

    # LOCATION
    province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    barangay = db.Column(db.String(100))
    full_address = db.Column(db.Text)

    # PRODUCT INFO
    product = db.Column(db.String(100))
    weight = db.Column(db.Float)

    # PRICE SYSTEM
    suggested_price = db.Column(db.Float)

    # ADMIN PRICE CONTROL
    admin_note = db.Column(db.Text)
    resubmitted_price = db.Column(db.Float)

    # STATUS FLOW
    status = db.Column(
        db.String(50),
        default="pending_price"
    )

    # TIMESTAMP
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<WeighLog {self.product} - {self.status}>"