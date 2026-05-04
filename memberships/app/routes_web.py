from flask import Blueprint, render_template, request, redirect, url_for, flash

from .db import (
    get_all_memberships,
    get_total_monthly_cost,
    get_upcoming_renewals,
    add_membership,
    update_membership,
    delete_membership_by_id
)

web = Blueprint('memberships_web', __name__,
                template_folder='templates',
                static_folder='static')


@web.route("/")
def index():
    try:
        memberships     = get_all_memberships()
        monthly_costs   = get_total_monthly_cost()
        yearly_costs    = {curr: amount * 12 for curr, amount in monthly_costs.items()}
        upcoming        = get_upcoming_renewals(days=30)
    except Exception as e:
        flash(f"Error: {e}", "error")
        memberships   = []
        monthly_costs = {}
        yearly_costs  = {}
        upcoming      = []

    return render_template("memberships/index.html",
                           memberships=memberships,
                           monthly_costs=monthly_costs,
                           yearly_costs=yearly_costs,
                           upcoming=upcoming)


@web.route("/add", methods=["POST"])
def handle_add_membership():
    organization    = request.form.get("organization", "").strip()
    description     = request.form.get("description", "").strip()
    membership_type = request.form.get("membership_type", "").strip()
    member_since    = request.form.get("member_since")
    is_paid         = request.form.get("is_paid") == "1"
    renewal_date    = request.form.get("renewal_date") or None

    raw_price = request.form.get("price_per_period")
    frequency = request.form.get("payment_frequency") or None
    currency  = request.form.get("currency", "").strip().upper() or None

    if not (organization and membership_type and member_since):
        flash("Organization, Type, and Member Since are required.", "warning")
        return redirect(url_for("memberships_web.index"))

    try:
        price = float(raw_price) if raw_price else None
        add_membership(organization, description, membership_type,
                       member_since, is_paid, frequency, price, currency, renewal_date)
        flash(f"Added membership: {organization}.", "success")

    except ValueError:
        flash("Price must be a valid number.", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")

    return redirect(url_for("memberships_web.index"))


@web.route("/edit/<int:membership_id>", methods=["POST"])
def handle_edit_membership(membership_id):
    organization    = request.form.get("organization", "").strip()
    description     = request.form.get("description", "").strip()
    membership_type = request.form.get("membership_type", "").strip()
    member_since    = request.form.get("member_since")
    is_paid         = request.form.get("is_paid") == "1"
    renewal_date    = request.form.get("renewal_date") or None

    raw_price = request.form.get("price_per_period")
    frequency = request.form.get("payment_frequency") or None
    currency  = request.form.get("currency", "").strip().upper() or None

    if not (organization and membership_type and member_since):
        flash("Organization, Type, and Member Since are required.", "warning")
        return redirect(url_for("memberships_web.index"))

    try:
        price = float(raw_price) if raw_price else None
        update_membership(membership_id, organization, description, membership_type,
                          member_since, is_paid, frequency, price, currency, renewal_date)
        flash(f"Updated membership: {organization}.", "success")

    except ValueError:
        flash("Price must be a valid number.", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")

    return redirect(url_for("memberships_web.index"))


@web.route("/delete/<int:membership_id>", methods=["POST"])
def handle_delete_membership(membership_id):
    try:
        delete_membership_by_id(membership_id)
        flash("Membership deleted.", "success")
    except Exception as e:
        flash(f"Error deleting membership: {e}", "error")

    return redirect(url_for("memberships_web.index"))