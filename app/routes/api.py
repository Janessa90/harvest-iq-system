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
# Dashboard → Hardware trigger
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

    # Set weighing flag
    user.is_weighing = True
    db.session.commit()

    print(f"[API] Start weighing triggered for Farmer ID: {farmer_id}")

    return jsonify({
        "status": "started",
        "farmer_id": farmer_id
    })


# ─────────────────────────
# CHECK WEIGHING
# Hardware polling endpoint
# ─────────────────────────
@api_bp.route("/check-weighing/<int:farmer_id>")
def check_weighing(farmer_id):

    user = User.query.get(farmer_id)

    if user and user.is_weighing:
        return jsonify({"weighing": True})

    return jsonify({"weighing": False})


# ─────────────────────────
# SUBMIT WEIGHT
# Hardware → Database
# ─────────────────────────
@api_bp.route("/submit-weight", methods=["POST"])
def submit_weight():

    data = request.get_json() or {}

    print("[API] Incoming weight data:", data)

    farmer_id = data.get("farmer_id")
    weight = data.get("weight")

    if not farmer_id or weight is None:
        return jsonify({"error": "Missing data"}), 400

    farmer = User.query.get(farmer_id)

    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    try:
        weight_value = float(weight)
    except:
        return jsonify({"error": "Invalid weight value"}), 400

    # Create weigh log
    log = WeighLog(
        farmer_id=farmer.id,
        farmer_name=farmer.username,
        phone=farmer.phone,
        province=farmer.province,
        city=farmer.city,
        barangay=farmer.barangay,
        full_address=farmer.full_address,
        product=farmer.main_product,
        suggested_price=farmer.price_per_kg,
        weight=weight_value,
        status="pending"
    )

    # Reset weighing flag
    farmer.is_weighing = False

    db.session.add(log)
    db.session.commit()

    print(f"[API] Weight saved → Farmer {farmer.id} | {weight_value} kg")

    return jsonify({
        "message": "Weight submitted successfully",
        "farmer_id": farmer.id,
        "weight": weight_value
    })