from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash
)
from flask_login import login_required, current_user
from app import db
from app.models.weigh_logs import WeighLog

farmer_bp = Blueprint(
    "farmer",
    __name__,
    url_prefix="/farmer"
)

# ─────────────────────────────────────
# FARMER DASHBOARD
# ─────────────────────────────────────
@farmer_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("farmer/dashboard.html")


# ─────────────────────────────────────
# START WEIGHING
# ─────────────────────────────────────
@farmer_bp.route("/start-weighing", methods=["POST"])
@login_required
def start_weighing():

    weight = request.form.get("weight")

    if not weight:
        flash("Weight is required.", "danger")
        return redirect(url_for("farmer.dashboard"))

    log = WeighLog(
        farmer_id=current_user.id,
        farmer_name=current_user.username,
        weight=float(weight),
        status="pending"
    )

    db.session.add(log)
    db.session.commit()

    print("Saved successfully")

    flash("Weight submitted for admin approval.", "success")
    return redirect(url_for("farmer.dashboard"))