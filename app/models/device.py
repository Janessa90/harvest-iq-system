from app import db

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    weighing = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Device {self.id} weighing={self.weighing}>"