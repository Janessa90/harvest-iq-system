from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.weigh_logs import WeighLog

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


# ─────────────────────────────────────────────
# START WEIGHING (Farmer → ESP32 trigger)
# ─────────────────────────────────────────────
@api_bp.route("/start-weighing", methods=["POST"])
@login_required
def start_weighing():

    if current_user.role != "farmer":
        return jsonify({
            "error": "Unauthorized"
        }), 403

    return jsonify({
        "message": "Weighing started",
        "farmer_id": current_user.id
    })


# ─────────────────────────────────────────────
# SUBMIT WEIGHT (ESP32 → Server)
# ─────────────────────────────────────────────
@api_bp.route("/submit-weight", methods=["POST"])
def submit_weight():

    data = request.json

    farmer_id = data.get("farmer_id")
    product_name = data.get("product_name")
    weight = data.get("weight")

    log = WeighLog(
        farmer_id=farmer_id,
        product_name=product_name,
        weight_kg=weight,
        status="pending"
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({
        "message": "Weight submitted successfully"
    })