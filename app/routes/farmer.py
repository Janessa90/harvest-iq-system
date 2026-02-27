from flask import (
    Blueprint, render_template,
    request, redirect, url_for, flash
)
from flask_login import login_required, current_user
from app import db
from app.models.weigh_logs import WeighLog

# ✅ FIX: name → _name_
farmer_bp = Blueprint(
    "farmer",
     __name__,
    url_prefix="/farmer"
)


# ======================================================
# FARMER DASHBOARD
# ======================================================
@farmer_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("farmer/dashboard.html")


# ======================================================
# VIEW REJECTED LOGS
# ======================================================
@farmer_bp.route("/rejected")
@login_required
def rejected_logs():

    logs = WeighLog.query.filter_by(
        farmer_id=current_user.id,
        status="price_rejected"
    ).all()

    return render_template(
        "farmer/rejected_logs.html",
        logs=logs
    )


# ======================================================
# RESUBMIT PRICE
# ======================================================
@farmer_bp.route("/resubmit/<int:log_id>", methods=["POST"])
@login_required
def resubmit_price(log_id):

    log = WeighLog.query.get_or_404(log_id)

    # ✅ FIX: correct form field name
    new_price = request.form.get("new_price")

    try:
        log.resubmitted_price = float(new_price)
        log.status = "resubmitted"
        db.session.commit()
        flash("Price resubmitted to admin.", "success")
    except Exception:
        flash("Invalid price.", "danger")

    return redirect(url_for("farmer.rejected_logs"))