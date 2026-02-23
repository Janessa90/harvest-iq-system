from flask import Blueprint, request, jsonify
from app import db
from app.models.weigh_logs import WeighLog
from app.models.user import User

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)

# ─────────────────────────
# START WEIGHING
# ─────────────────────────
@api_bp.route("/start-weighing", methods=["POST"])
def start_weighing():

    data = request.get_json() or {}
    farmer_id = data.get("farmer_id")

    if not farmer_id:
        return jsonify({"error": "Missing farmer_id"}), 400

    user = User.query.get(farmer_id)

    if not user:
        return jsonify({"error": "Farmer not found"}), 404

    user.is_weighing = True
    db.session.commit()

    return jsonify({"status": "started"})


# ─────────────────────────
# CHECK WEIGHING
# ─────────────────────────
@api_bp.route("/check-weighing/<int:farmer_id>")
def check_weighing(farmer_id):

    user = User.query.get(farmer_id)

    if user and user.is_weighing:
        return jsonify({"weighing": True})

    return jsonify({"weighing": False})


# ─────────────────────────
# SUBMIT WEIGHT
# ─────────────────────────
@api_bp.route("/submit-weight", methods=["POST"])
def submit_weight():

    data = request.get_json() or {}

    farmer_id = data.get("farmer_id")
    weight = data.get("weight")

    if not farmer_id or weight is None:
        return jsonify({"error": "Missing data"}), 400

    farmer = User.query.get(farmer_id)

    log = WeighLog(
        farmer_id=farmer_id,
        product_name=farmer.main_product,  # ✅ AUTO PRODUCT
        weight_kg=weight,
        status="pending"
    )

    # RESET FLAG
    farmer.is_weighing = False

    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": "Weight submitted successfully"
    })