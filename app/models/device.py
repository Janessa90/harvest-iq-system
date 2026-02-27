from app import db


class Device(db.Model):
    _tablename_ = "device"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    mac_address = db.Column(db.String(100))

    weighing = db.Column(db.Boolean, default=False)

    current_farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    def __repr__(self):
        return f"<Device {self.id}>"