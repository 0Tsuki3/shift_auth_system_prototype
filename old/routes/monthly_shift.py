from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta
from utils.exclude_time_utils import load_exclude_data
from utils.shift_utils import load_shift_data_for_date

monthly_shift_bp = Blueprint("monthly_shift", __name__)

@monthly_shift_bp.route("/monthly_shift/<month>")
def monthly_shift(month):
    start_date = datetime.strptime(month + "-01", "%Y-%m-%d")
    date_list = []
    while start_date.strftime("%Y-%m") == month:
        date_list.append(start_date.strftime("%Y-%m-%d"))
        start_date += timedelta(days=1)

    exclude_data = load_exclude_data(month)

    all_data = []
    for date in date_list:
        shift_data = load_shift_data_for_date(date)
        exclude_today = [e for e in exclude_data if e["date"] == date]
        staff_names = sorted(set(s["name"] for s in shift_data))
        schedule = {name: {"shift": [], "exclude": []} for name in staff_names}

        for s in shift_data:
            schedule[s["name"]]["shift"].append((s["start"], s["end"]))
        for e in exclude_today:
            if e["name"] in schedule:
                schedule[e["name"]]["exclude"].append({
                    "start": e["start"],
                    "end": e["end"],
                    "category": e["category"]
                })

        all_data.append({"date": date, "schedule": schedule})

    is_admin = session.get("role") == "admin"
    account = session.get("account")
    if is_admin:
        home_url = url_for("admin.admin_home")
    elif account:
        home_url = url_for("staff.staff_home", account=account)
    else:
        home_url = url_for("auth.public_home")
    return render_template("monthly_shift.html", month=month, all_data=all_data, is_admin=is_admin, home_url=home_url)
