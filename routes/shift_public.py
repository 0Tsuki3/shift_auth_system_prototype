from flask import Blueprint, render_template, request
from datetime import datetime
from utils.staff_utils import load_staff, sort_staff_list, build_shift_dict
from utils.csv_utils import create_monthly_csv_templates, load_shifts
from utils.date_utils import generate_short_date_labels

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
