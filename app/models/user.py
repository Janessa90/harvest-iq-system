from app import db, bcrypt
from flask_login import UserMixin


class User(db.Model, UserMixin):
    _tablename_ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # LOGIN
    username = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # ROLE
    role = db.Column(db.String(50), default="buyer")
    status = db.Column(db.String(50), default="approved")

    # PROFILE
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(50))

    province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    barangay = db.Column(db.String(100))
    full_address = db.Column(db.Text)

    # FARMER PRODUCT INFO
    main_product = db.Column(db.String(100))
    price_per_kg = db.Column(db.Float, default=0)

    # START WEIGHING FLAG
    is_weighing = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    # PASSWORD
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)