from flask import Blueprint, request, jsonify
from app import db
from app.models.weigh_logs import WeighLog
from app.models.user import User
from app.models.device import Device
from app.models.weigh_session import WeighSession

api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)

# =====================================================
# DEVICE CONFIG
# =====================================================
DEVICE_ID = 6
ACTIVE_FARMER_ID = None


# =====================================================
# START WEIGHING
# =====================================================
@api_bp.route("/start-weighing", methods=["POST"])
def start_weighing():
    global ACTIVE_FARMER_ID

    data = request.get_json() or {}

    farmer_id = data.get("farmer_id")
    product_name = data.get("product_name")
    price_value = data.get("price")

    if not farmer_id:
        return jsonify({"error": "Missing farmer_id"}), 400

    farmer = User.query.get(farmer_id)
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    # remember active farmer
    ACTIVE_FARMER_ID = farmer_id

    # ============================================
    # SAVE ACTIVE PRODUCT SESSION (DB BASED)
    # ============================================
    WeighSession.query.filter_by(
        farmer_id=farmer_id,
        is_active=True
    ).update({"is_active": False})

    new_session = WeighSession(
        farmer_id=farmer_id,
        product_name=product_name,
        price=price_value,
        is_active=True
    )

    db.session.add(new_session)

    # ============================================
    # TURN ON DEVICE
    # ============================================
    device = Device.query.get(DEVICE_ID)

    if device:
        device.weighing = True
    else:
        device = Device(
            id=DEVICE_ID,
            name="Main Scale",
            weighing=True
        )
        db.session.add(device)

    db.session.commit()

    return jsonify({"status": "started"})


# =====================================================
# STOP WEIGHING
# =====================================================
@api_bp.route("/stop-weighing", methods=["POST"])
def stop_weighing():
    global ACTIVE_FARMER_ID

    device = Device.query.get(DEVICE_ID)
    if device:
        device.weighing = False

    ACTIVE_FARMER_ID = None
    db.session.commit()

    return jsonify({"status": "stopped"})


# =====================================================
# ESP CHECK COMMAND
# =====================================================
@api_bp.route("/check-weighing/<int:device_id>")
def check_weighing(device_id):

    device = Device.query.get(device_id)

    if device and device.weighing:
        return jsonify({"weighing": True})

    return jsonify({"weighing": False})


# =====================================================
# SUBMIT FINAL WEIGHT
# =====================================================
@api_bp.route("/submit-weight", methods=["POST"])
def submit_weight():
    global ACTIVE_FARMER_ID

    data = request.get_json() or {}
    weight = data.get("weight")

    print("[API] Incoming weight:", data)

    if ACTIVE_FARMER_ID is None:
        return jsonify({"error": "No active farmer"}), 400

    farmer = User.query.get(ACTIVE_FARMER_ID)

    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    # validate weight
    try:
        weight_value = float(weight)
    except:
        return jsonify({"error": "Invalid weight"}), 400

    if weight_value <= 0:
        return jsonify({"error": "Weight must be > 0"}), 400

    # ============================================
    # GET ACTIVE PRODUCT SESSION
    # ============================================
    weigh_session = WeighSession.query.filter_by(
        farmer_id=farmer.id,
        is_active=True
    ).first()

    if weigh_session:
        product_name = weigh_session.product_name
        price_value = weigh_session.price
    else:
        product_name = "Unknown Product"
        price_value = 0

    # ============================================
    # SAVE WEIGH LOG
    # ============================================
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

    db.session.add(log)

    # stop device
    device = Device.query.get(DEVICE_ID)
    if device:
        device.weighing = False

    ACTIVE_FARMER_ID = None

    db.session.commit()

    print(
        f"[API] SAVED → Farmer {farmer.id} | "
        f"{product_name} | {weight_value} kg"
    )

    return jsonify({
        "message": "Weight submitted successfully"
    })