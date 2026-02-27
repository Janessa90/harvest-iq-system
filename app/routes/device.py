from flask import Blueprint, request, jsonify
from datetime import datetime

from app import db
from app.models.device import Device
from app.models.user import User
from app.models.weigh_session import WeighSession
from app.models.weigh_logs import WeighLog


device_bp = Blueprint(
    "device_api",
    __name__,
    url_prefix="/api"
)

# =====================================================
# ESP32 CHECK IF WEIGHING STARTED
# =====================================================
@device_bp.route("/check-weighing/<int:device_id>")
def check_weighing(device_id):

    device = Device.query.get(device_id)

    if device and device.weighing:
        return jsonify({
            "weighing": True,
            "farmer_id": device.current_farmer_id
        })

    return jsonify({
        "weighing": False
    })

# =====================================================
# ESP32 SEND WEIGHT
# =====================================================
@device_bp.route("/submit-weight", methods=["POST"])
def submit_weight():

    try:
        data = request.get_json(force=True)

        weight = float(data.get("weight", 0))

        if weight <= 0:
            return jsonify({
                "error": "Invalid weight"
            }), 400


        # ✅ GET ACTIVE DEVICE
        device = Device.query.get(1)

        if not device or not device.current_farmer_id:
            return jsonify({
                "error": "No active weighing"
            }), 400


        farmer = User.query.get(device.current_farmer_id)

        # ✅ GET ACTIVE SESSION
        session = WeighSession.query.filter_by(
            farmer_id=farmer.id,
            is_active=True
        ).first()

        if not session:
            return jsonify({
                "error": "No active session"
            }), 400


        # ✅ SAVE WEIGH LOG
        log = WeighLog(
            farmer_id=farmer.id,
            farmer_name=farmer.username,
            product=session.product_name,
            suggested_price=session.price,
            weight=weight,
            status="pending_price",
            created_at=datetime.utcnow()
        )

        db.session.add(log)

        # ✅ AUTO STOP DEVICE
        device.weighing = False
        device.current_farmer_id = None
        session.is_active = False

        db.session.commit()

        print("✅ WEIGHT RECEIVED:", weight)

        return jsonify({
            "message": "Weight saved"
        })

    except Exception as e:
        db.session.rollback()
        print("❌ DEVICE ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# =====================================================
# OPTIONAL MANUAL CONTROL
# =====================================================
@device_bp.route("/force-stop/<int:device_id>")
def force_stop(device_id):

    device = Device.query.get(device_id)

    if device:
        device.weighing = False
        device.current_farmer_id = None
        db.session.commit()

    return jsonify({
        "message": "Device stopped"
    })