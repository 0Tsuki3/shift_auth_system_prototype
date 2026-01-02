from flask import Blueprint, render_template, request
from datetime import datetime
from utils.staff_utils import load_staff, sort_staff_list, build_shift_dict
from utils.csv_utils import create_monthly_csv_templates, load_shifts
from utils.date_utils import generate_short_date_labels
from utils.graph_utils import generate_all_day_view
from utils.date_utils import get_current_month




shift_public_bp = Blueprint('shift_public', __name__, url_prefix='/shift')


@shift_public_bp.route("/view")
def view_shift_public():
    month = request.args.get("month", datetime.today().strftime("%Y-%m"))
    create_monthly_csv_templates(month)

    staff_list = sort_staff_list(load_staff())
    date_map = generate_short_date_labels(month)
    dates = [d["date"] for d in date_map]

    shifts = build_shift_dict(load_shifts(month), staff_list)

    all_staff = []
    for staff in staff_list:
        shift_dict = {}
        for date in dates:
            entries = []
            if staff["name"] in shifts and date in shifts[staff["name"]]:
                for start, end in shifts[staff["name"]][date].values():
                    entries.append({"start": start, "end": end})
            if entries:
                shift_dict[date] = entries
        all_staff.append({
            "name": staff["name"],
            "shifts": shift_dict
        })

    return render_template(
        "view_all_readonly.html",  # 今staffで使ってるのと全く同じ
        month=month,
        date_map=date_map,
        all_staff=all_staff,
        account=None  # ログインなし
    )


@shift_public_bp.route("/view_timeline_public")
def view_timeline_public():
    month = request.args.get("month", get_current_month())
    all_data = generate_all_day_view(month)

    return render_template("view_timeline_readonly.html", month=month, all_data=all_data)




# routes/shift_public.py

from flask import Blueprint, render_template
from utils.csv_utils import load_shifts
from utils.staff_utils import load_staff
from utils.date_utils import generate_short_date_labels
from utils.graph_utils import generate_vertical_graph_data_admin, calculate_daily_labor_cost, calculate_daily_work_hours


@shift_public_bp.route("/graph/readonly")
def vertical_graph_readonly():
    from datetime import datetime
    from utils.csv_utils import load_notes
    
    month = datetime.now().strftime("%Y-%m")
    
    staff_list = load_staff()
    shift_list = load_shifts(month)
    graph_data, _ = generate_vertical_graph_data_admin(month)
    date_labels = generate_short_date_labels(month)
    daily_cost = calculate_daily_labor_cost(shift_list, staff_list)
    daily_hours = calculate_daily_work_hours(shift_list, staff_list)
    notes = load_notes(month)

    return render_template("vertical_graph_staff.html",
                           graph_data=graph_data,
                           date_labels=date_labels,
                           daily_cost=daily_cost,
                           daily_hours=daily_hours,
                           notes=notes)
