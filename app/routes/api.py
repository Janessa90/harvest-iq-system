from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.device import Device
from app.models.weigh_session import WeighSession
from app.models.weigh_logs import WeighLog

api_bp = Blueprint("api", __name__, url_prefix="/api")


# =====================================================
# START WEIGHING
# =====================================================
@api_bp.route("/start-weighing", methods=["POST"])
@login_required
def start_weighing():

    try:
        data = request.get_json(force=True)

        product = data.get("product_name")
        price = data.get("price")

        if not product or not price:
            return jsonify({"error": "Missing data"}), 400


        farmer_id = current_user.id

        # deactivate old
        WeighSession.query.update({"is_active": False})

        session = WeighSession(
            farmer_id=farmer_id,
            product_name=product,
            price=price,
            is_active=True
        )

        db.session.add(session)

        device = Device.query.get(1)

        if not device:
            device = Device(
                id=1,
                name="ESP32",
                weighing=True,
                current_farmer_id=farmer_id
            )
            db.session.add(device)
        else:
            device.weighing = True
            device.current_farmer_id = farmer_id

        db.session.commit()

        print("✅ DEVICE UPDATED:", farmer_id)

        return jsonify({
            "status": "started"
        })

    except Exception as e:
        db.session.rollback()
        print("❌ START ERROR:", e)
        return jsonify({"error": str(e)}), 500


# =====================================================
# STOP
# =====================================================
@api_bp.route("/stop-weighing", methods=["POST"])
@login_required
def stop_weighing():

    device = Device.query.get(1)

    if device:
        device.weighing = False
        device.current_farmer_id = None
        db.session.commit()

    return jsonify({"status": "stopped"})