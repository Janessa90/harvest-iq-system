from flask import Blueprint, request, jsonify
from app import db
from app.models.weigh_logs import WeighLog
from app.models.user import User
from app.models.device import Device

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)

# =====================================================
# 🔥 CONFIG — MUST MATCH YOUR ESP
# =====================================================
DEVICE_ID = 6  # ⚠️ ESP uses FARMER_ID = 6 → treated as device id

# holds which farmer owns the next weight
ACTIVE_FARMER_ID = None


# =====================================================
# START WEIGHING (Farmer clicks button)
# =====================================================
@api_bp.route("/start-weighing", methods=["POST"])
def start_weighing():
    global ACTIVE_FARMER_ID

    data = request.get_json() or {}
    farmer_id = data.get("farmer_id")

    if not farmer_id:
        return jsonify({"error": "Missing farmer_id"}), 400

    farmer = User.query.get(farmer_id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    # ✅ remember who started weighing
    ACTIVE_FARMER_ID = farmer_id

    # ✅ TURN ON THE SCALE (CRITICAL)
    device = Device.query.get(DEVICE_ID)
    if device:
        device.weighing = True
    else:
        # auto-create if missing (safety)
        device = Device(id=DEVICE_ID, name="Main Scale", weighing=True)
        db.session.add(device)

    db.session.commit()

    print(f"[API] START → Farmer {farmer_id} | Device {DEVICE_ID}")

    return jsonify({"status": "started"})


# =====================================================
# STOP WEIGHING (manual stop button)
# =====================================================
@api_bp.route("/stop-weighing", methods=["POST"])
def stop_weighing():
    global ACTIVE_FARMER_ID

    device = Device.query.get(DEVICE_ID)
    if device:
        device.weighing = False

    ACTIVE_FARMER_ID = None
    db.session.commit()

    print("[API] STOP weighing")

    return jsonify({"status": "stopped"})


# =====================================================
# ESP POLLING ENDPOINT
# =====================================================
@api_bp.route("/check-weighing/<int:device_id>")
def check_weighing(device_id):

    device = Device.query.get(device_id)

    if device and device.weighing:
        return jsonify({"weighing": True})

    return jsonify({"weighing": False})


# =====================================================
# ESP SENDS FINAL WEIGHT
# =====================================================
@api_bp.route("/submit-weight", methods=["POST"])
def submit_weight():
    global ACTIVE_FARMER_ID

    data = request.get_json() or {}
    weight = data.get("weight")

    print("[API] Incoming weight:", data)

    # must have active farmer
    if ACTIVE_FARMER_ID is None:
        return jsonify({"error": "No active farmer"}), 400

    farmer = User.query.get(ACTIVE_FARMER_ID)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    try:
        weight_value = float(weight)
    except Exception:
        return jsonify({"error": "Invalid weight"}), 400

    if weight_value <= 0:
        return jsonify({"error": "Weight must be > 0"}), 400

    # =========================================
    # build product info from farmer profile
    # =========================================
    product_name = farmer.main_product or "Unnamed Product"
    price_value = farmer.price_per_kg or 0

    log = WeighLog(
        farmer_id=farmer.id,
        farmer_name=farmer.username,
        phone=farmer.phone,
        province=farmer.province,
        city=farmer.city,
        barangay=farmer.barangay,
        full_address=farmer.full_address,
        product=product_name,
        suggested_price=price_value,
        weight=weight_value,
        status="pending"
    )

    # ✅ STOP DEVICE AFTER SUCCESS
    device = Device.query.get(DEVICE_ID)
    if device:
        device.weighing = False

    ACTIVE_FARMER_ID = None

    db.session.add(log)
    db.session.commit()

    print(f"[API] SAVED → Farmer {farmer.id} | {weight_value} kg")

    return jsonify({"message": "Weight submitted successfully"})